import pickle, os, requests
movies = pickle.load(open(r'C:\Users\LENOVO\OneDrive\Desktop\5th sem-AI ML Misssion\Projects\Movie Recommendation System\movies.pkl', 'rb'))
row = movies[movies['title'] == 'Fight Club'].iloc[0]
print('Movie ID from pickle:', row['movie_id'])
print('Title:', row['title'])
api_key = os.getenv('TMDB_API_KEY')
print('API key from env:', api_key[:4] + '...' if api_key else 'None')
if api_key:
    url = f'https://api.themoviedb.org/3/movie/{row["movie_id"]}?api_key={api_key}&language=en-US'
    print('Request URL (key hidden):', url.split('?')[0] + '?api_key=****&language=en-US')
    try:
        r = requests.get(url, timeout=10)
        print('Status code:', r.status_code)
        if r.status_code == 200:
            data = r.json()
            print('Response keys:', list(data.keys()))
            print('Poster path:', data.get('poster_path'))
        else:
            print('Error response:', r.text)
    except Exception as e:
        print('Exception:', e)
