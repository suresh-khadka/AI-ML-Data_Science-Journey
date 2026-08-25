from sentence_transformers import SentenceTransformer
import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st

@st.cache_resource
def get_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

@st.cache_data
def get_data():
    movies = pickle.load(open('movies_final.pkl', 'rb'))
    meta = pickle.load(open('meta.pkl', 'rb'))
    movie_embeddings = pickle.load(open('sbert_embeddings.pkl', 'rb'))  # precomputed, not recalculated
    return movies, meta, movie_embeddings

def retrieve_movies(question, top_k=8):
    """
    Retrieve top-k movies similar to a user question using SBERT embeddings.
    """
    model = get_model()
    movies, meta, movie_embeddings = get_data()

    # Only encode the question (fast, single string) — never re-encode all movies
    question_embedding = model.encode([question])

    sims = cosine_similarity(question_embedding, movie_embeddings)[0]
    top_indices = np.argsort(sims)[::-1][:top_k]

    results = []
    for idx in top_indices:
        movie_id = movies.iloc[idx]['movie_id']
        meta_row = meta[meta['movie_id'] == movie_id]
        if not meta_row.empty:
            row = meta_row.iloc[0]
            results.append({
                'title': row.get('title', movies.iloc[idx]['title']),
                'overview': row.get('overview', 'N/A'),
                'release_date': row.get('release_date', 'Unknown'),
                'genres': row.get('genre_list', []) if isinstance(row.get('genre_list'), list) else [],
                'rating': float(row.get('vote_average', 0.0)),
                'runtime': row.get('runtime', 'N/A'),
            })
        else:
            results.append({
                'title': movies.iloc[idx]['title'],
                'genres': [],
                'rating': 0.0
            })
    return results

if __name__ == '__main__':
    q = "a thrilling adventure movie with superheroes"
    print(retrieve_movies(q, top_k=5))