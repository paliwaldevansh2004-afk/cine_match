"""
Model Building Script for Movie Recommendation System
Precomputes and serializes:
1. movies_list.pkl: Clean metadata dataframe for quick UI lookups
2. top_matches.pkl: Precomputed Top-30 most similar movie indices & similarity scores
3. cv_model.pkl: Fitted CountVectorizer model
Optimized for production and low memory footprint in Streamlit!
"""

import os
import pickle
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data', 'processed')
MODELS_DIR = os.path.join(BASE_DIR, 'models')
os.makedirs(MODELS_DIR, exist_ok=True)

def build_recommender():
    print("--> Loading processed movies data...")
    csv_path = os.path.join(DATA_DIR, 'movies_recommender.csv')
    df = pd.read_csv(csv_path)
    print(f"    Loaded {len(df)} movies.")

    print("--> Vectorizing text tags using TF-IDF (Term Frequency - Inverse Document Frequency)...")
    # Using TfidfVectorizer with 6000 top features and removing English stop words
    tfidf = TfidfVectorizer(max_features=6000, stop_words='english')
    vectors = tfidf.fit_transform(df['tags']).astype(np.float32)

    print("--> Precomputing Top-30 neighbors for all movies...")
    # To keep memory footprint minimal and queries instantaneous:
    # Instead of saving a 600MB dense matrix, we store the top 30 neighbors per movie
    top_matches = {}
    
    # Process in chunks of 500 for high speed and low memory usage
    chunk_size = 500
    n_movies = vectors.shape[0]

    for start in range(0, n_movies, chunk_size):
        end = min(start + chunk_size, n_movies)
        chunk_sim = cosine_similarity(vectors[start:end], vectors)  # shape (chunk_size, n_movies)
        
        for i in range(chunk_sim.shape[0]):
            global_idx = start + i
            # Top 35 indices (excluding itself at rank 0)
            sorted_indices = chunk_sim[i].argsort()[::-1]
            # Exclude self
            sorted_indices = [idx for idx in sorted_indices if idx != global_idx][:30]
            scores = [round(float(chunk_sim[i][idx]), 3) for idx in sorted_indices]
            
            top_matches[global_idx] = {
                'indices': sorted_indices,
                'scores': scores
            }

    print(f"    Top matches precomputed for all {len(top_matches)} titles.")

    # Save artifacts
    movies_pkl = os.path.join(MODELS_DIR, 'movies_list.pkl')
    matches_pkl = os.path.join(MODELS_DIR, 'top_matches.pkl')
    tfidf_pkl = os.path.join(MODELS_DIR, 'tfidf_model.pkl')

    print("--> Saving serialized artifacts to models/ directory...")
    # Clean dataframe for app
    df_clean = df[['movie_id', 'tmdb_id', 'title', 'industry', 'release_year', 'primary_genre', 'rating', 'director', 'top_cast', 'poster_url', 'overview']].copy()
    
    with open(movies_pkl, 'wb') as f:
        pickle.dump(df_clean, f)
    print(f"    Saved: {movies_pkl} ({os.path.getsize(movies_pkl) / 1024:.1f} KB)")

    with open(matches_pkl, 'wb') as f:
        pickle.dump(top_matches, f)
    print(f"    Saved: {matches_pkl} ({os.path.getsize(matches_pkl) / (1024*1024):.2f} MB)")

    with open(tfidf_pkl, 'wb') as f:
        pickle.dump(tfidf, f)
    print(f"    Saved: {tfidf_pkl} ({os.path.getsize(tfidf_pkl) / 1024:.1f} KB)")

    print("\n[SUCCESS] Model training and precomputation completed successfully!")

if __name__ == '__main__':
    build_recommender()
