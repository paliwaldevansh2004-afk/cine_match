"""
Data Preprocessing Script for Movie Recommendation System & Power BI Dashboard
Author: Fresher Data Scientist / Analyst Portfolio
Workflow:
1. Load Hollywood (TMDB 5000) & Bollywood (TIMDB) datasets
2. Handle missing values, parse JSON strings & pipe-delimited text
3. Feature Engineering: Profit, ROI, Decades, Primary Genre, Tags
4. Unify schemas into a single master dataset
5. Export clean data for Power BI and NLP Recommender
"""

import os
import ast
import json
import re
import pandas as pd
import numpy as np

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')
os.makedirs(PROCESSED_DIR, exist_ok=True)


def parse_json_column(text, key='name', max_items=None):
    """Safely parse JSON-formatted string column (used for TMDB)."""
    if pd.isna(text):
        return []
    try:
        data = ast.literal_eval(text)
        if isinstance(data, list):
            items = [item[key] for item in data if isinstance(item, dict) and key in item]
            if max_items:
                items = items[:max_items]
            return items
    except Exception:
        pass
    return []


def clean_text(text):
    """Basic text normalization for NLP tags."""
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def get_decade(year):
    """Map release year to decade category for Power BI trend analysis."""
    try:
        y = int(year)
        if y < 1970:
            return "Pre-1970s"
        elif y < 1980:
            return "1970s"
        elif y < 1990:
            return "1980s"
        elif y < 2000:
            return "1990s"
        elif y < 2010:
            return "2000s"
        elif y < 2020:
            return "2010s"
        else:
            return "2020s"
    except Exception:
        return "Unknown"


def categorize_rating(rating):
    """Categorize IMDb/TMDB rating for business analysis."""
    try:
        r = float(rating)
        if r >= 8.0:
            return "All-Time Classic (8.0+)"
        elif r >= 7.0:
            return "Highly Rated (7.0 - 7.9)"
        elif r >= 6.0:
            return "Average (6.0 - 6.9)"
        elif r > 0:
            return "Low Rated (< 6.0)"
    except Exception:
        pass
    return "Not Rated"


def process_hollywood():
    """Load and process TMDB 5000 Movies & Credits."""
    print("--> Processing Hollywood (TMDB 5000) dataset...")
    movies_path = os.path.join(DATA_DIR, 'tmdb_5000_movies.csv')
    credits_path = os.path.join(DATA_DIR, 'tmdb_5000_credits.csv')

    df_movies = pd.read_csv(movies_path)
    df_credits = pd.read_csv(credits_path)

    # Merge on title / id
    df_merged = df_movies.merge(df_credits, left_on='id', right_on='movie_id', suffixes=('', '_credit'))

    records = []
    for _, row in df_merged.iterrows():
        title = str(row['title']).strip()
        if not title:
            continue

        # Extract genres & keywords
        genres = parse_json_column(row['genres'])
        keywords = parse_json_column(row['keywords'], max_items=5)
        
        # Extract cast (top 3 actors)
        cast = parse_json_column(row['cast'], max_items=3)
        
        # Extract director from crew
        director = "Unknown"
        try:
            crew_list = ast.literal_eval(row['crew'])
            for member in crew_list:
                if member.get('job') == 'Director':
                    director = member.get('name', 'Unknown')
                    break
        except Exception:
            pass

        # Release year
        release_date = str(row['release_date'])
        year = release_date[:4] if len(release_date) >= 4 and release_date[:4].isdigit() else np.nan

        # Financials
        budget = float(row['budget']) if pd.notna(row['budget']) and row['budget'] > 0 else np.nan
        revenue = float(row['revenue']) if pd.notna(row['revenue']) and row['revenue'] > 0 else np.nan
        profit = (revenue - budget) if (pd.notna(budget) and pd.notna(revenue)) else np.nan
        roi = round(((profit / budget) * 100), 2) if (pd.notna(budget) and pd.notna(profit) and budget > 0) else np.nan

        overview = str(row['overview']) if pd.notna(row['overview']) else ""
        rating = float(row['vote_average']) if pd.notna(row['vote_average']) else 0.0
        votes = int(row['vote_count']) if pd.notna(row['vote_count']) else 0
        runtime = int(row['runtime']) if pd.notna(row['runtime']) and row['runtime'] > 0 else np.nan

        # Combined NLP tags for Recommender
        tag_components = [
            clean_text(overview),
            " ".join([clean_text(g) for g in genres]),
            " ".join([clean_text(k) for k in keywords]),
            " ".join([clean_text(c.replace(" ", "")) for c in cast]),  # samworthington
            clean_text(director.replace(" ", ""))                      # jamescameron
        ]
        tags = " ".join([t for t in tag_components if t])

        records.append({
            'movie_id': f"hw_{row['id']}",
            'tmdb_id': int(row['id']),
            'title': title,
            'industry': 'Hollywood',
            'release_year': year,
            'primary_genre': genres[0] if genres else 'Drama',
            'genres': ", ".join(genres) if genres else 'Drama',
            'director': director,
            'top_cast': ", ".join(cast) if cast else 'Unknown',
            'rating': round(rating, 1),
            'votes': votes,
            'runtime_mins': runtime,
            'budget_usd': budget,
            'revenue_usd': revenue,
            'profit_usd': profit,
            'roi_percentage': roi,
            'overview': overview,
            'poster_url': "",  # Will be fetched via TMDB API or fallback in app
            'tags': tags
        })

    df_hw = pd.DataFrame(records)
    print(f"    Hollywood processed: {len(df_hw)} movies")
    return df_hw


def process_bollywood():
    """Load and process Bollywood (TIMDB) dataset."""
    print("--> Processing Bollywood (TIMDB) dataset...")
    bolly_path = os.path.join(DATA_DIR, 'bollywood_full.csv')
    crew_path = os.path.join(DATA_DIR, 'bollywood_crew.csv')
    crew_data_path = os.path.join(DATA_DIR, 'bollywood_crew_data.csv')

    df_bolly = pd.read_csv(bolly_path)
    
    # Build director mapping from crew files
    director_lookup = {}
    if os.path.exists(crew_path) and os.path.exists(crew_data_path):
        df_crew = pd.read_csv(crew_path)
        df_crew_data = pd.read_csv(crew_data_path)
        name_map = dict(zip(df_crew_data['crew_id'], df_crew_data['name']))
        
        for _, r in df_crew.iterrows():
            imdb_id = str(r['imdb_id']).strip()
            dirs = str(r['directors'])
            if pd.notna(dirs) and dirs != '\\N':
                first_dir_id = dirs.split('|')[0]
                if first_dir_id in name_map:
                    director_lookup[imdb_id] = name_map[first_dir_id]

    records = []
    for _, row in df_bolly.iterrows():
        title = str(row['title_x']).strip()
        if not title or title.lower() == 'nan':
            continue

        imdb_id = str(row['imdb_id']).strip()

        # Genres (pipe-separated: Action|Drama)
        raw_genres = str(row['genres'])
        genres = [g.strip() for g in raw_genres.split('|') if g.strip() and g != '\\N'] if pd.notna(raw_genres) else []
        
        # Actors (pipe-separated: Vicky Kaushal|Paresh Rawal|)
        raw_actors = str(row['actors'])
        actors = [a.strip() for a in raw_actors.split('|') if a.strip() and a != '\\N'][:3] if pd.notna(raw_actors) else []

        # Director
        director = director_lookup.get(imdb_id, "Unknown")

        # Year
        year_raw = row['year_of_release']
        year = str(int(year_raw)) if pd.notna(year_raw) and str(year_raw).isdigit() else np.nan

        # Rating & votes
        rating = float(row['imdb_rating']) if pd.notna(row['imdb_rating']) else 0.0
        votes_raw = str(row['imdb_votes']).replace(',', '') if pd.notna(row['imdb_votes']) else '0'
        votes = int(votes_raw) if votes_raw.isdigit() else 0

        # Runtime
        runtime_raw = str(row['runtime']).replace('min', '').strip() if pd.notna(row['runtime']) else ''
        runtime = int(runtime_raw) if runtime_raw.isdigit() else np.nan

        # Overview
        overview = str(row['summary']) if pd.notna(row['summary']) and str(row['summary']).strip() != '\\N' else ""
        if not overview and pd.notna(row['story']):
            overview = str(row['story']).strip()

        # Poster path from TIMDB (already direct Wikimedia link)
        poster_url = str(row['poster_path']) if pd.notna(row['poster_path']) and row['poster_path'].startswith('http') else ""

        # Combined NLP tags for Recommender
        tag_components = [
            clean_text(overview),
            " ".join([clean_text(g) for g in genres]),
            " ".join([clean_text(a.replace(" ", "")) for a in actors]),  # shahrukhkhan
            clean_text(director.replace(" ", ""))                       # rajkumarhirani
        ]
        tags = " ".join([t for t in tag_components if t])

        records.append({
            'movie_id': f"bw_{imdb_id}",
            'tmdb_id': np.nan,
            'title': title,
            'industry': 'Bollywood',
            'release_year': year,
            'primary_genre': genres[0] if genres else 'Drama',
            'genres': ", ".join(genres) if genres else 'Drama',
            'director': director,
            'top_cast': ", ".join(actors) if actors else 'Unknown',
            'rating': round(rating, 1),
            'votes': votes,
            'runtime_mins': runtime,
            'budget_usd': np.nan,  # Marked as NaN for clean Power BI filtering
            'revenue_usd': np.nan,
            'profit_usd': np.nan,
            'roi_percentage': np.nan,
            'overview': overview,
            'poster_url': poster_url,
            'tags': tags
        })

    df_bw = pd.DataFrame(records)
    # Deduplicate titles
    df_bw = df_bw.drop_duplicates(subset=['title', 'release_year'])
    print(f"    Bollywood processed: {len(df_bw)} movies")
    return df_bw


def main():
    print("=========================================================")
    print("  MOVIE RECOMMENDER & POWER BI ETL PIPELINE (START)      ")
    print("=========================================================")

    # 1. Process datasets
    df_hw = process_hollywood()
    df_bw = process_bollywood()

    # 2. Combine into master DataFrame
    print("\n--> Merging Hollywood and Bollywood datasets...")
    df_all = pd.concat([df_hw, df_bw], ignore_index=True)

    # 3. Additional Feature Engineering
    print("--> Applying feature engineering (Decades, Rating Category, Profit Margin)...")
    df_all['decade'] = df_all['release_year'].apply(get_decade)
    df_all['rating_category'] = df_all['rating'].apply(categorize_rating)
    df_all['has_financial_data'] = df_all['budget_usd'].notna() & df_all['revenue_usd'].notna()
    
    # Sort by rating and votes for quality presentation
    df_all = df_all.sort_values(by=['votes', 'rating'], ascending=False).reset_index(drop=True)

    print(f"    Total Combined Movies: {len(df_all)}")
    print(f"    - Hollywood: {(df_all['industry'] == 'Hollywood').sum()}")
    print(f"    - Bollywood: {(df_all['industry'] == 'Bollywood').sum()}")

    # 4. Export for Power BI
    pbi_path = os.path.join(PROCESSED_DIR, 'movies_powerbi.csv')
    cols_pbi = [
        'movie_id', 'title', 'industry', 'release_year', 'decade',
        'primary_genre', 'genres', 'director', 'top_cast',
        'rating', 'rating_category', 'votes', 'runtime_mins',
        'budget_usd', 'revenue_usd', 'profit_usd', 'roi_percentage',
        'has_financial_data'
    ]
    df_all[cols_pbi].to_csv(pbi_path, index=False)
    print(f"\n[OK] Power BI dataset saved to: {pbi_path}")
    print(f"     Columns exported: {len(cols_pbi)}")

    # 5. Export for Recommender
    rec_path = os.path.join(PROCESSED_DIR, 'movies_recommender.csv')
    cols_rec = [
        'movie_id', 'tmdb_id', 'title', 'industry', 'release_year',
        'primary_genre', 'rating', 'director', 'top_cast',
        'poster_url', 'overview', 'tags'
    ]
    # Filter out movies with completely empty tags
    df_rec = df_all[df_all['tags'].str.len() > 5][cols_rec].copy()
    df_rec.to_csv(rec_path, index=False)
    print(f"[OK] Recommender dataset saved to: {rec_path}")
    print(f"     Movies available for recommendation: {len(df_rec)}")
    print("=========================================================")
    print("  ETL PIPELINE COMPLETED SUCCESSFULLY!                   ")
    print("=========================================================")


if __name__ == '__main__':
    main()
