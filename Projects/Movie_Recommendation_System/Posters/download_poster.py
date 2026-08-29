import os
import pickle
import requests
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTER_DIR = os.path.join(BASE_DIR, 'posters')
os.makedirs(POSTER_DIR, exist_ok=True)

TMDB_API_KEY = os.getenv('TMDB_API_KEY')  # reuse the one you already use for the recommender tab

movies = pickle.load(open(os.path.join(BASE_DIR, 'movies_final.pkl'), 'rb'))

downloaded = []
for _, row in movies.iterrows():
    movie_id = row['movie_id']
    save_path = os.path.join(POSTER_DIR, f"{movie_id}.jpg")
    if os.path.exists(save_path):
        downloaded.append(movie_id)
        continue
    try:
        r = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}",
                          params={"api_key": TMDB_API_KEY})
        data = r.json()
        poster_path = data.get('poster_path')
        if poster_path:
            img_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
            img_data = requests.get(img_url).content
            with open(save_path, 'wb') as f:
                f.write(img_data)
            downloaded.append(movie_id)
        time.sleep(0.05)  # be polite to TMDB's API
    except Exception as e:
        print(f"Failed for {movie_id}: {e}")

print(f"Downloaded {len(downloaded)} posters.")
pickle.dump(downloaded, open(os.path.join(BASE_DIR, 'movies_with_posters.pkl'), 'wb'))