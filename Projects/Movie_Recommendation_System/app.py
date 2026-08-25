import streamlit as st
import pickle
import requests
import os

# Load .env file if exists
def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key] = value.strip('"').strip("'")

load_env()

# Set page config
st.set_page_config(layout="wide", page_title="Movie Recommender")

# Load data with caching
@st.cache_resource
def load_data():
    movies = pickle.load(open('movies_final.pkl', 'rb'))
    similarity = pickle.load(open('similarity_sbert.pkl', 'rb'))
    meta = pickle.load(open('meta.pkl', 'rb'))  # loaded for potential use
    return movies, similarity, meta

movies, similarity, meta = load_data()

# Get TMDB API key from secrets or environment
def get_api_key():
    # Try Streamlit secrets first (for Streamlit Cloud)
    try:
        if hasattr(st, 'secrets') and 'tmdb_api_key' in st.secrets:
            return st.secrets['tmdb_api_key']
    except:
        pass
    # Fallback to environment variable
    return os.getenv('TMDB_API_KEY')

API_KEY = get_api_key()

# Placeholder image URL for missing posters
PLACEHOLDER_POSTER = "https://placehold.co/500x750/222/fff?text=No+Poster"

def fetch_poster(movie_id):
    """Fetch movie poster from TMDB API."""
    if not API_KEY:
        st.error("TMDB API key not found. Check .env or secrets.")
        print("DEBUG: TMDB API key is empty or None")
        return PLACEHOLDER_POSTER
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        # st.write(f"Fetching poster for movie_id {movie_id}")
        # st.write(f"Request URL (key hidden): https://api.themoviedb.org/3/movie/{movie_id}?api_key=****&language=en-US")
        print(f"DEBUG: Request URL (key hidden): https://api.themoviedb.org/3/movie/{movie_id}?api_key=****&language=en-US")
        response = requests.get(url, timeout=5)
        # st.write(f"Response status code: {response.status_code}")
        print(f"DEBUG: Response status code: {response.status_code}")
        response.raise_for_status()
        data = response.json()
        # st.write(f"Response keys: {list(data.keys())}")
        print(f"DEBUG: Response keys: {list(data.keys())}")
        poster_path = data.get('poster_path')
        if poster_path:
            poster_url = f"https://image.tmdb.org/t/p/w500/{poster_path}"
            # st.write(f"Poster URL: {poster_url}")
            print(f"DEBUG: Poster URL: {poster_url}")
            return poster_url
        else:
            st.write(f"No poster_path in response for movie_id {movie_id}: {data}")
            print(f"DEBUG: No poster_path in response for movie_id {movie_id}: {data}")
            return PLACEHOLDER_POSTER
    except requests.exceptions.HTTPError as http_err:
        st.write(f"HTTP error for movie_id {movie_id}: {http_err}")
        print(f"DEBUG: HTTP error for movie_id {movie_id}: {http_err}")
        return PLACEHOLDER_POSTER
    except Exception as err:
        st.write(f"Error fetching poster for movie_id {movie_id}: {err}")
        print(f"DEBUG: Error fetching poster for movie_id {movie_id}: {err}")
        return PLACEHOLDER_POSTER

def recommend_movies_reranked(title, movies_df, sim_matrix, meta_df, top_n=5, candidate_pool=20, weight=0.3):
    idx = movies_df[movies_df["title"] == title].index[0]
    distances = sim_matrix[idx]
    candidates = sorted(enumerate(distances), key=lambda x: x[1], reverse=True)[1:candidate_pool+1]

    results = []
    for i, sim_score in candidates:
        movie_id = movies_df.iloc[i]["movie_id"]
        # Safely get popularity with fallback
        try:
            pop_series = meta_df.loc[meta_df["movie_id"] == movie_id, "popularity"]
            pop = pop_series.values[0] if len(pop_series) > 0 else 0.0
        except (KeyError, IndexError):
            pop = 0.0  # Default popularity if not found
        results.append((movies_df.iloc[i]["title"], sim_score, pop))

    max_pop = max(r[2] for r in results) or 1
    reranked = sorted(results, key=lambda r: (1 - weight) * r[1] + weight * (r[2] / max_pop), reverse=True)
    return [r[0] for r in reranked[:top_n]]

# Import chatbot function
from chatbot import ask_chatbot

# App UI with tabs
tab1, tab2 = st.tabs(["Recommender", "Ask about movies"])

with tab1:
    st.title("Movie Recommender System")
    # Searchable dropdown
    selected_movie = st.selectbox(
        "Select a movie",
        options=movies['title'].values,
        index=0
    )

    # Recommend button
    if st.button("Recommend", type="primary", use_container_width=True):
        with st.spinner("Finding recommendations..."):
            recommended_titles = recommend_movies_reranked(selected_movie, movies, similarity, meta, top_n=5)
            # Get movie ids in the same order
            title_to_id = dict(zip(movies['title'], movies['movie_id']))
            recommended_ids = [title_to_id[title] for title in recommended_titles]

        if recommended_titles:
            # Display results in 5 columns
            cols = st.columns(5)
            for col, title, movie_id in zip(cols, recommended_titles, recommended_ids):
                with col:
                    poster_url = fetch_poster(movie_id)
                    st.image(poster_url, use_container_width=True)
                    st.caption(title)

with tab2:
    st.header("Ask about movies")
    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    # Display chat messages
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    # User input
    if prompt := st.chat_input("Ask about movies..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Convert session state messages to chat history format expected by ask_chatbot
                # Map roles: "assistant" -> "model" for Gemini compatibility
                history = []
                for m in st.session_state.chat_history:
                    role = m["role"]
                    if role == "assistant":
                        role = "model"
                    history.append({"role": role, "parts": [m["content"]]})
                answer, timings = ask_chatbot(prompt, chat_history=history)
                st.markdown(answer)
                st.caption(f"⏱️ {timings['total']:.1f}s via {timings['provider']} "f"(retrieval: {timings['retrieval']:.1f}s, generation: {timings['gemini_call']:.1f}s)")
        # Add assistant message to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": answer})