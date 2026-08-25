# Movie Recommender System

A Streamlit web app that recommends movies based on similarity in tags/content.

## Features
- Searchable dropdown to select a movie
- Get top 5 similar movies with posters fetched from TMDB
- Clean, minimal UI
- Error handling for missing posters and API failures

## Setup
1. Install dependencies:
   ```bash
   pip install streamlit pandas requests
   ```
2. Get a TMDB API key from [https://www.themoviedb.org/settings/api](https://www.themoviedb.org/settings/api)
3. Create a `.env` file in the project root with:
   ```
   TMDB_API_KEY=your_api_key_here
   ```
   Alternatively, you can set the environment variable or use Streamlit secrets.

## Run
```bash
streamlit run app.py
```

## Files
- `app.py`: Main application
- `movies.pkl`: Pickled DataFrame with movie data
- `similarity.pkl`: Pickled cosine similarity matrix
- `tfidf.pkl`: Fitted TfidfVectorizer (loaded but not used in inference)
- `.env`: Environment variables (not committed to version control)

## Notes
- The app loads the pickled data once at startup using `st.cache_resource`
- Posters are fetched from TMDB API in real-time with a fallback placeholder
- UI is designed to be simple and functional