import os
import pickle
import random
import numpy as np
from PIL import Image, ImageFilter
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POSTER_DIR = os.path.join(BASE_DIR, 'posters')

@st.cache_data
def load_game_data():
    movies = pickle.load(open(os.path.join(BASE_DIR, 'movies_final.pkl'), 'rb'))
    downloaded = pickle.load(open(os.path.join(BASE_DIR, 'movies_with_posters.pkl'), 'rb'))
    poster_embeddings = pickle.load(open(os.path.join(BASE_DIR, 'poster_embeddings.pkl'), 'rb'))
    playable_movies = movies[movies['movie_id'].isin(downloaded)]
    return playable_movies, poster_embeddings

def get_blurred_poster(movie_id, reveal_level):
    path = os.path.join(POSTER_DIR, f"{movie_id}.jpg")
    img = Image.open(path).convert('RGB')
    blur_radius = max(0, 24 - reveal_level * 6)
    return img.filter(ImageFilter.GaussianBlur(blur_radius)) if blur_radius > 0 else img

def get_visual_hint(movie_id, poster_embeddings, playable_movies):
    if movie_id not in poster_embeddings:
        return None
    target_emb = poster_embeddings[movie_id].reshape(1, -1)
    other_ids = [mid for mid in poster_embeddings if mid != movie_id]
    other_embs = np.array([poster_embeddings[mid] for mid in other_ids])
    sims = cosine_similarity(target_emb, other_embs)[0]
    best_idx = np.argmax(sims)
    best_id = other_ids[best_idx]
    row = playable_movies[playable_movies['movie_id'] == best_id]
    return row.iloc[0]['title'] if not row.empty else None

def start_new_round(playable_movies):
    row = playable_movies.sample(1).iloc[0]
    st.session_state.game_movie_id = row['movie_id']
    st.session_state.game_movie_title = row['title']
    st.session_state.game_reveal_level = 0
    st.session_state.game_guesses = 0
    st.session_state.game_won = False
    st.session_state.game_hint_used = False