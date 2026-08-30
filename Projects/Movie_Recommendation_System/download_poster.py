import os
import pickle
import requests
import time
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POSTER_DIR = os.path.join(BASE_DIR, 'posters')
os.makedirs(POSTER_DIR, exist_ok=True)

TMDB_API_KEY = os.getenv('TMDB_API_KEY')
if not TMDB_API_KEY:
    raise ValueError("TMDB_API_KEY not found in .env")

movies = pickle.load(open(os.path.join(BASE_DIR, 'movies_final.pkl'), 'rb'))
print(f"Loaded {len(movies)} movies. Starting download...")

downloaded = []
for _, row in tqdm(movies.iterrows(), total=len(movies), desc="Downloading posters"):
    movie_id = row['movie_id']
    save_path = os.path.join(POSTER_DIR, f"{movie_id}.jpg")
    if os.path.exists(save_path):
        downloaded.append(movie_id)
        continue
    try:
        r = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}",
            params={"api_key": TMDB_API_KEY},
            timeout=10
        )
        data = r.json()

        # Check for API errors explicitly instead of assuming poster_path is just missing
        if r.status_code != 200:
            print(f"  ✗ API error {r.status_code} for {movie_id}: {data.get('status_message', 'unknown')}")
            continue

        poster_path = data.get('poster_path')
        if poster_path:
            img_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
            img_data = requests.get(img_url, timeout=10).content
            with open(save_path, 'wb') as f:
                f.write(img_data)
            downloaded.append(movie_id)
        else:
            print(f"  ✗ No poster_path for {movie_id} (movie exists but has no poster)")
    except Exception as e:
        print(f"  ✗ Exception for {movie_id}: {e}")

print(f"Downloaded {len(downloaded)} posters.")
pickle.dump(downloaded, open(os.path.join(BASE_DIR, 'movies_with_posters.pkl'), 'wb'))