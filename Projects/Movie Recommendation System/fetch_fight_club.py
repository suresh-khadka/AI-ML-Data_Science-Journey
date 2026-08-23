import os
import pickle
import requests
import pandas as pd

# Load the movies.pkl
with open('movies.pkl', 'rb') as f:
    df = pickle.load(f)

# Find the row for 'Fight Club'
row = df[df['title'] == 'Fight Club']
if row.empty:
    print("Movie 'Fight Club' not found")
    exit(1)

movie_id = row.iloc[0]['movie_id']
print(f"Found movie_id: {movie_id}")

# Get API key from environment
api_key = os.getenv('TMDB_API_KEY')
if not api_key:
    print("TMDB_API_KEY environment variable not set")
    exit(1)

# Make request to TMDB API
url = f"https://api.themoviedb.org/3/movie/{movie_id}"
params = {'api_key': api_key}
response = requests.get(url, params=params)

print(f"Response status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"JSON keys: {list(data.keys())}")
    if 'poster_path' in data:
        print(f"Poster path: {data['poster_path']}")
else:
    print(f"Error: {response.text}")