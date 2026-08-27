from sentence_transformers import SentenceTransformer
import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_resource
def get_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

@st.cache_data
def get_data():
    movies = pickle.load(open(os.path.join(BASE_DIR, 'movies_final.pkl'), 'rb'))
    meta = pickle.load(open(os.path.join(BASE_DIR, 'meta.pkl'), 'rb'))
    movie_embeddings = pickle.load(open(os.path.join(BASE_DIR, 'sbert_embeddings.pkl'), 'rb'))
    return movies, meta, movie_embeddings


import re

def retrieve_movies(question, top_k=8):
    """
    Retrieve top-k movies similar to a user question using SBERT embeddings,
    with exact title matching and deterministic year/genre filtering applied first.
    """
    model = get_model()
    movies, meta, movie_embeddings = get_data()

    question_lower = question.lower()
    results = []
    matched_indices = set()

    def build_result(idx, meta_row=None):
        if meta_row is not None and not meta_row.empty:
            row = meta_row.iloc[0]
            return {
                'title': row.get('title', movies.iloc[idx]['title']),
                'overview': row.get('overview', 'N/A'),
                'release_date': row.get('release_date', 'Unknown'),
                'genres': row.get('genre_list', []) if isinstance(row.get('genre_list'), list) else [],
                'rating': float(row.get('vote_average', 0.0)),
                'runtime': row.get('runtime', 'N/A'),
            }
        else:
            return {
                'title': movies.iloc[idx]['title'],
                'genres': [],
                'rating': 0.0
            }

    # 1. Exact/near title match first
    title_matches = movies[movies['title'].str.lower().apply(lambda t: t in question_lower)]
    if not title_matches.empty:
        for idx in title_matches.index:
            matched_indices.add(idx)
            movie_id = movies.loc[idx, 'movie_id']
            meta_row = meta[meta['movie_id'] == movie_id]
            results.append(build_result(idx, meta_row))

    # 2. Deterministic year/genre filtering
    year_matches = re.findall(r'\b(19\d{2}|20\d{2})\b', question)
    genre_keywords = ['comedy', 'action', 'drama', 'horror', 'romance', 'sci-fi',
                       'science fiction', 'thriller', 'animation', 'fantasy', 'crime',
                       'mystery', 'adventure', 'family', 'war', 'documentary']
    detected_genre = next((g for g in genre_keywords if g in question_lower), None)

    if year_matches or detected_genre:
        filtered_meta = meta.copy()

        if year_matches:
            years = [int(y) for y in year_matches]
            if len(years) == 1:
                if '0s' in question_lower:
                    lo, hi = years[0], years[0] + 9
                else:
                    lo, hi = years[0], years[0]
            else:
                lo, hi = min(years), max(years)
            filtered_meta = filtered_meta[
                filtered_meta['release_date'].astype(str).str[:4].apply(
                    lambda y: y.isdigit() and lo <= int(y) <= hi
                )
            ]

        if detected_genre:
            filtered_meta = filtered_meta[filtered_meta['genre_list'].apply(
                lambda gl: any(detected_genre.lower() in x.lower() for x in gl) if isinstance(gl, list) else False
            )]

        if len(filtered_meta) > 0:
            filtered_meta = filtered_meta.sort_values('vote_average', ascending=False).head(top_k)
            for _, meta_row_single in filtered_meta.iterrows():
                movie_row = movies[movies['movie_id'] == meta_row_single['movie_id']]
                if movie_row.empty:
                    continue
                idx = movie_row.index[0]
                if idx in matched_indices:
                    continue
                matched_indices.add(idx)
                results.append(build_result(idx, meta[meta['movie_id'] == meta_row_single['movie_id']]))

    # 3. Fill remaining slots with semantic similarity search
    if len(results) < top_k:
        question_embedding = model.encode([question])
        sims = cosine_similarity(question_embedding, movie_embeddings)[0]
        top_indices = np.argsort(sims)[::-1]

        for idx in top_indices:
            if len(results) >= top_k:
                break
            if idx in matched_indices:
                continue
            movie_id = movies.iloc[idx]['movie_id']
            meta_row = meta[meta['movie_id'] == movie_id]
            results.append(build_result(idx, meta_row))
            matched_indices.add(idx)

    return results

    return results
if __name__ == '__main__':
    q = "a thrilling adventure movie with superheroes"
    print(retrieve_movies(q, top_k=5))