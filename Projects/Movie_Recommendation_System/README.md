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

## Attention-Aware Playback (Local Proof-of-Concept)
A new tab "🎥 Attention-Aware Playback" has been added as a local-only proof-of-concept feature.
This module uses your webcam to monitor attention while playing a sample video and automatically
pauses playback when it detects:
- 😴 SLEEPING: Eyes closed for sustained period
- 👀 DISTRACTED: Head turned away from screen  
- 🚶 ABSENT: No face detected (you left the frame)

**Important:** This feature runs locally only and requires additional dependencies.
It will not work in cloud deployments (like Streamlit Community Cloud) due to reliance on
continuous webcam processing.

To enable this feature:
1. Install the required dependencies:
   ```bash
   pip install mediapipe streamlit-webrtc opencv-python-headless av numpy
   ```
   Or if you have the requirements file:
   ```bash
   pip install -r requirements-attention.txt
   ```
2. Run the app normally: `streamlit run app.py`
3. Click on the "🎥 Attention-Aware Playback" tab
4. Allow webcam access when prompted by your browser

The feature uses BigBuckBunny_512kb.mp4 as a sample video file (already included in the project).