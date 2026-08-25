import os
import pickle
import requests

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

# Load data
movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Get TMDB API key from environment
API_KEY = os.getenv('TMDB_API_KEY')
PLACEHOLDER_POSTER = "https://placehold.co/500x750/222/fff?text=No+Poster"

def fetch_poster(movie_id):
    """Fetch movie poster from TMDB API."""
    if not API_KEY:
        print("ERROR: TMDB API key not found. Check .env or secrets.")
        return PLACEHOLDER_POSTER
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        print(f"Fetching poster for movie_id {movie_id}")
        print(f"Request URL (key hidden): https://api.themoviedb.org/3/movie/{movie_id}?api_key=****&language=en-US")
        response = requests.get(url, timeout=5)
        print(f"Response status code: {response.status_code}")
        response.raise_for_status()
        data = response.json()
        print(f"Response keys: {list(data.keys())}")
        poster_path = data.get('poster_path')
        if poster_path:
            poster_url = f"https://image.tmdb.org/t/p/w500/{poster_path}"
            print(f"Poster URL: {poster_url}")
            return poster_url
        else:
            print(f"No poster_path in response for movie_id {movie_id}: {data}")
            return PLACEHOLDER_POSTER
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error for movie_id {movie_id}: {http_err}")
        return PLACEHOLDER_POSTER
    except Exception as err:
        print(f"Error fetching poster for movie_id {movie_id}: {err}")
        return PLACEHOLDER_POSTER

# Test with Fight Club's movie_id (we know from earlier it's 550)
print("=== Testing with movie_id 550 (Fight Club) ===")
poster_url = fetch_poster(550)
print(f"Result: {poster_url}")

# Now, let's test the recommendation flow for a sample movie
def recommend(movie_title):
    try:
        idx = movies[movies['title'] == movie_title].index[0]
    except IndexError:
        print("Movie not found in database.")
        return [], []
    sim_scores = list(enumerate(similarity[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    top_indices = [i[0] for i in sim_scores[1:6]]
    recommended_titles = movies.iloc[top_indices]['title'].tolist()
    recommended_ids = movies.iloc[top_indices]['movie_id'].tolist()
    return recommended_titles, recommended_ids

print("\n=== Testing recommendation for 'Fight Club' ===")
titles, ids = recommend('Fight Club')
print(f"Recommended titles: {titles}")
print(f"Recommended IDs: {ids}")
for movie_id in ids:
    print(f"\nFetching poster for movie_id {movie_id}:")
    poster_url = fetch_poster(movie_id)
    print(f"Result: {poster_url}")