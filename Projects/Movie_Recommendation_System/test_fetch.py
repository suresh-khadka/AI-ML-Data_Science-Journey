import pickle

def fetch_poster(movie_id):
    # Placeholder: replace with actual fetch logic
    # For demonstration, just return a dummy URL or None
    print(f"[DEBUG] Fetching poster for movie_id: {movie_id}")
    # Simulate possible error
    if movie_id is None:
        print("[ERROR] movie_id is None")
        return None
    # Example: construct a fake poster URL
    poster_url = f"https://example.com/posters/{movie_id}.jpg"
    print(f"[INFO] Poster URL: {poster_url}")
    return poster_url

def main():
    # Load movies data
    try:
        with open('movies.pkl', 'rb') as f:
            movies = pickle.load(f)
    except FileNotFoundError:
        print("[ERROR] movies.pkl not found")
        return
    except Exception as e:
        print(f"[ERROR] Failed to load movies.pkl: {e}")
        return

    # Assuming movies is a DataFrame with columns 'title' and 'movie_id'
    # Try to find the movie_id for 'Fight Club'
    try:
        # If movies is a DataFrame
        if hasattr(movies, 'shape'):
            # pandas DataFrame
            movie_row = movies[movies['title'] == 'Fight Club']
            if not movie_row.empty:
                movie_id = movie_row.iloc[0]['movie_id']
            else:
                print("[ERROR] Movie 'Fight Club' not found")
                return
        else:
            # Assume it's a list of dicts or similar
            movie_id = None
            for m in movies:
                if m.get('title') == 'Fight Club':
                    movie_id = m.get('movie_id')
                    break
            if movie_id is None:
                print("[ERROR] Movie 'Fight Club' not found")
                return
    except Exception as e:
        print(f"[ERROR] Error while searching for movie: {e}")
        return

    print(f"[INFO] Found movie_id for Fight Club: {movie_id}")
    poster_url = fetch_poster(movie_id)
    print(f"[RESULT] Poster URL: {poster_url}")

if __name__ == "__main__":
    main()