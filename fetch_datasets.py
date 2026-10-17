import os
import requests
import pandas as pd

DATA_DIR = r"C:\Users\paliw\.gemini\antigravity\scratch\movie_recommender_system\data"
os.makedirs(DATA_DIR, exist_ok=True)

def download_file(url, target_path):
    print(f"Downloading from {url}...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers, stream=True)
    if r.status_code == 200:
        with open(target_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Saved: {target_path} (Size: {os.path.getsize(target_path)} bytes)")
        return True
    else:
        print(f"Failed with status code {r.status_code}")
        return False

# 1. TMDB 5000
tmdb_movies_url = "https://raw.githubusercontent.com/yajasarora/Movie-Recommendation-Model-using-NLP-Techniques/main/tmdb_5000_movies.csv"
tmdb_credits_url = "https://raw.githubusercontent.com/yajasarora/Movie-Recommendation-Model-using-NLP-Techniques/main/tmdb_5000_credits.csv"

tmdb_movies_path = os.path.join(DATA_DIR, "tmdb_5000_movies.csv")
tmdb_credits_path = os.path.join(DATA_DIR, "tmdb_5000_credits.csv")

if not os.path.exists(tmdb_movies_path):
    download_file(tmdb_movies_url, tmdb_movies_path)
if not os.path.exists(tmdb_credits_path):
    download_file(tmdb_credits_url, tmdb_credits_path)

# 2. Bollywood TIMDB
bollywood_url = "https://raw.githubusercontent.com/pncnmnp/TIMDB/master/1950-2019/bollywood_full.csv"
bollywood_path = os.path.join(DATA_DIR, "bollywood_full.csv")

if not os.path.exists(bollywood_path):
    download_file(bollywood_url, bollywood_path)

print("\n--- Inspecting Data ---")
if os.path.exists(tmdb_movies_path):
    df_tmdb = pd.read_csv(tmdb_movies_path, nrows=3)
    print("TMDB Movies columns:", list(df_tmdb.columns))

if os.path.exists(tmdb_credits_path):
    df_credits = pd.read_csv(tmdb_credits_path, nrows=3)
    print("TMDB Credits columns:", list(df_credits.columns))

if os.path.exists(bollywood_path):
    df_bolly = pd.read_csv(bollywood_path, nrows=3)
    print("Bollywood columns:", list(df_bolly.columns))
    print(df_bolly.head(1))
