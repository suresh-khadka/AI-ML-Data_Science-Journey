import os
import time
import google.generativeai as genai
from groq import Groq
from retrieve_movies import retrieve_movies
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("Google API key not found. Set GOOGLE_API_KEY or GEMINI_API_KEY in environment or .env")
genai.configure(api_key=api_key)

# Stable, low-latency model instead of gemini-3.6-flash
model = genai.GenerativeModel('gemini-3.6-flash')

# Groq client (fallback when Gemini quota is exceeded)
groq_api_key = os.getenv('GROQ_API_KEY')
groq_client = Groq(api_key=groq_api_key) if groq_api_key else None

def ask_chatbot(question, chat_history=None):
    timings = {}
    t0 = time.time()

    # 1. Retrieve relevant movies
    movies = retrieve_movies(question, top_k=50)  
    timings['retrieval'] = time.time() - t0

    # 2. Format context
    t1 = time.time()
    context_lines = []
    for m in movies:
        genres = ', '.join(m['genres']) if m['genres'] else 'N/A'
        context_lines.append(f"- {m['title']} ({m['release_date']}) | Genres: {', '.join(m['genres'])} | "f"Rating: {m['rating']:.1f} | Runtime: {m['runtime']} min\n"
            f"  Overview: {m['overview']}"
        )
    context_block = "\n".join(context_lines)

    system_instr = (
    "Answer the user's question using the movie data provided below. "
    "You may make reasonable inferences about tone, mood, or theme (e.g. "
    "'heartwarming', 'dark', 'feel-good') based on the plot overview and genres — "
    "you don't need those exact words to appear in the data. "
    "However, do NOT invent factual details that aren't in the data, such as release dates, "
    "cast, awards, or plot events not mentioned in the overview. "
    "IMPORTANT: The data provided below is a small SAMPLE retrieved specifically for this "
    "question, not the full dataset. A differently-phrased question may retrieve a different "
    "subset of movies. Never claim something 'does not exist in the dataset' or 'the dataset "
    "has no X' — only say it wasn't found among the movies shown to you this turn. "
    "If your answer in this turn seems to contradict something you said earlier in the "
    "conversation, explain the discrepancy honestly (e.g. different questions retrieve "
    "different movie subsets) rather than ignoring or hiding the earlier answer. "
    "If the movies shown to you this turn truly lack relevant options (e.g. wrong genre, "
    "wrong era), say so honestly, but phrase it as 'none of the retrieved movies matched' "
    "rather than 'the dataset does not contain'."
    "If the user's spelling of a title seems close to a real movie's title, assume they meant "
    "that movie, even with minor typos."
    "When the data provided represents a true full-dataset ranking (e.g. for 'highest rated' "
    "or 'most popular' questions), you may state the result with confidence."
    "When reporting 'highest rated' movies, note that ratings reflect TMDB user scores and results "
    "exclude movies with very few votes to avoid statistical outliers."
    )

    user_prompt = f"""Context:
{context_block}

Question: {question}"""

    if chat_history is None:
        chat_history = []

    chat = model.start_chat(history=chat_history)
    full_prompt = f"{system_instr}\n\n{user_prompt}"
    timings['prompt_build'] = time.time() - t1

    # 3. Call Gemini, fall back to Groq if quota/rate limit hit
    t2 = time.time()
    used_provider = "gemini"
    try:
        response = chat.send_message(full_prompt)
        answer = response.text
    except Exception as e:
        err_str = str(e)
        if ("429" in err_str or "quota" in err_str.lower()) and groq_client:
            try:
                completion = groq_client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[{"role": "user", "content": full_prompt}],
                )
                answer = completion.choices[0].message.content
                used_provider = "groq (Gemini quota exceeded)"
            except Exception as e2:
                answer = f"Both providers failed. Gemini: {e} | Groq: {e2}"
                used_provider = "none"
        else:
            answer = f"Error generating response: {e}"
            used_provider = "none"
    timings['gemini_call'] = time.time() - t2
    timings['provider'] = used_provider

    timings['total'] = time.time() - t0

    # Print timing breakdown to terminal
    print(f"[TIMING] provider: {used_provider} | retrieval: {timings['retrieval']:.2f}s | "
          f"prompt_build: {timings['prompt_build']:.2f}s | "
          f"gemini_call: {timings['gemini_call']:.2f}s | "
          f"total: {timings['total']:.2f}s")

    return answer, timings

if __name__ == '__main__':
    answer, timings = ask_chatbot("What are some good sci-fi movies from the 2000s?")
    print(answer)
    print(timings)