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


def retrieve_movies(question, top_k=20):
    model = get_model()
    movies, meta, movie_embeddings = get_data()

    # 1. Check for exact/near title match first
    question_lower = question.lower()
    title_matches = movies[movies['title'].str.lower().apply(lambda t: t in question_lower)]

    results = []
    matched_indices = set()

    if not title_matches.empty:
        for idx in title_matches.index:
            matched_indices.add(idx)
            movie_id = movies.loc[idx, 'movie_id']
            meta_row = meta[meta['movie_id'] == movie_id]
            if not meta_row.empty:
                row = meta_row.iloc[0]
                results.append({
                    'title': movies.loc[idx, 'title'],
                    'overview': row.get('overview', 'N/A'),
                    'release_date': row.get('release_date', 'Unknown'),
                    'genres': row.get('genre_list', []) if isinstance(row.get('genre_list'), list) else [],
                    'rating': float(row.get('vote_average', 0.0)),
                    'runtime': row.get('runtime', 'N/A'),
                })

    # 2. Fill remaining slots with semantic similarity search
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
        if not meta_row.empty:
            row = meta_row.iloc[0]
            results.append({
                'title': movies.iloc[idx]['title'],
                'overview': row.get('overview', 'N/A'),
                'release_date': row.get('release_date', 'Unknown'),
                'genres': row.get('genre_list', []) if isinstance(row.get('genre_list'), list) else [],
                'rating': float(row.get('vote_average', 0.0)),
                'runtime': row.get('runtime', 'N/A'),
            })

    return results
if __name__ == '__main__':
    q = "a thrilling adventure movie with superheroes"
    print(retrieve_movies(q, top_k=5))