import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

df = pd.read_csv(r'data\processed\movies_recommender.csv')
print(f"Loaded {len(df)} movies.")

cv = CountVectorizer(max_features=6000, stop_words='english')
vectors = cv.fit_transform(df['tags']).toarray()
print(f"Vector matrix created: {vectors.shape}")

def test_recommend(movie_title, top_n=5):
    matches = df[df['title'].str.lower() == movie_title.lower()]
    if matches.empty:
        matches = df[df['title'].str.lower().str.contains(movie_title.lower(), na=False)]
        if matches.empty:
            print(f"Not found: {movie_title}")
            return
    idx = matches.index[0]
    m_info = df.iloc[idx]
    print(f"\nTarget Movie: '{m_info['title']}' [{m_info['industry']}, {m_info['primary_genre']}, Rating: {m_info['rating']}]")

    sim_scores = cosine_similarity([vectors[idx]], vectors)[0]
    top_indices = sim_scores.argsort()[::-1][1:top_n+1]

    for rank, i in enumerate(top_indices, 1):
        r = df.iloc[i]
        print(f"   {rank}. {r['title']} ({r['industry']}, {r['release_year']}) - Rating: {r['rating']} - Similarity: {sim_scores[i]:.2f}")

test_recommend('The Dark Knight')
test_recommend('Inception')
test_recommend('Uri: The Surgical Strike')
test_recommend('3 Idiots')
test_recommend('Dangal')
