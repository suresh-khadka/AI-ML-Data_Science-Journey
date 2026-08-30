# import os
# from dotenv import load_dotenv
# from groq import Groq

# load_dotenv()
# client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# models = client.models.list()
# for m in models.data:
#     print(m.id) 


# import pickle
# meta = pickle.load(open('meta.pkl', 'rb'))
# print(meta.sort_values('vote_average', ascending=False).head(10)[['movie_id', 'vote_average']]) 

# print(detect_superlative("give me highest rating movies"))
# print(detect_superlative("highest rated movies"))
# print(detect_superlative("what is the best movie"))


import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()
TMDB_API_KEY = os.getenv('TMDB_API_KEY')
print("Key loaded:", TMDB_API_KEY)

start = time.time()
r = requests.get(
    "https://api.themoviedb.org/3/movie/19995",
    params={"api_key": TMDB_API_KEY},
    timeout=10
)
print("Time taken:", time.time() - start, "seconds")
print("Status:", r.status_code)
print(r.json())