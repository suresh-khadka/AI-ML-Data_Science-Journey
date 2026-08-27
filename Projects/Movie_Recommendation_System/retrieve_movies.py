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

superlative_keywords = {
    'highest rated': ('vote_average', False),
    'highest rating': ('vote_average', False),
    'highest-rated': ('vote_average', False),
    'top rated': ('vote_average', False),
    'top-rated': ('vote_average', False),
    'best rated': ('vote_average', False),
    'best': ('vote_average', False),
    'lowest rated': ('vote_average', True),
    'lowest rating': ('vote_average', True),
    'worst': ('vote_average', True),
    'most popular': ('popularity', False),
    'longest': ('runtime', False),
    'shortest': ('runtime', True),
}
def detect_superlative(question_lower):
    superlative_words = ['highest', 'top', 'best', 'greatest']
    inferior_words = ['lowest', 'worst']
    
    if any(w in question_lower for w in superlative_words) and 'rat' in question_lower:
        return 'vote_average', False
    if any(w in question_lower for w in inferior_words) and 'rat' in question_lower:
        return 'vote_average', True
    if 'popular' in question_lower and any(w in question_lower for w in superlative_words):
        return 'popularity', False
    if 'longest' in question_lower:
        return 'runtime', False
    if 'shortest' in question_lower:
        return 'runtime', True
    return None, None


def retrieve_movies(question, top_k=20):
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

    # 0. Handle superlative questions with a true full-dataset sort (bypasses everything below)
    column, ascending = detect_superlative(question_lower)
    if column:
        if column == 'vote_average':
            # Exclude low-vote-count outliers (e.g. a movie with 1 vote of 10.0)
            eligible = meta[meta['vote_count'] >= 50]
            sorted_meta = eligible.sort_values(column, ascending=ascending).head(top_k)
        else:
            sorted_meta = meta.sort_values(column, ascending=ascending).head(top_k)
        for _, meta_row_single in sorted_meta.iterrows():
            movie_row = movies[movies['movie_id'] == meta_row_single['movie_id']]
            if movie_row.empty:
                continue
            idx = movie_row.index[0]
            matched_indices.add(idx)
            results.append(build_result(idx, meta[meta['movie_id'] == meta_row_single['movie_id']]))
        return results

    # 1. Exact/near title match first
    from rapidfuzz import fuzz

# 1. Exact/near title match first (fuzzy, tolerant of typos)
    def title_in_question(title, question_lower, threshold=85):
        title_lower = title.lower()
        if title_lower in question_lower:
            return True
        # Check fuzzy match against sliding windows of the question
        words = question_lower.split()
        for window_size in range(1, min(len(title_lower.split()) + 2, len(words) + 1)):
            for i in range(len(words) - window_size + 1):
                phrase = ' '.join(words[i:i+window_size])
                if fuzz.ratio(title_lower, phrase) >= threshold:
                    return True
        return False

    title_matches = movies[movies['title'].apply(lambda t: title_in_question(t, question_lower))]
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

if __name__ == '__main__':
    q = "give me highest rating movies"
    results = retrieve_movies(q, top_k=20)
    for r in results:
        print(r['title'], r['rating'])

