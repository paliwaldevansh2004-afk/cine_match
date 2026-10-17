

import os
import pickle
import requests
import streamlit as st
import pandas as pd
import altair as alt

# Page Configuration
st.set_page_config(
    page_title="CineMatch - Movie Recommender & Analytics",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Dark Executive Theme)
st.markdown("""
<style>
    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #FF4B4B, #FF8533);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #999;
        margin-bottom: 20px;
    }
    .kpi-box {
        background-color: #1E222A;
        border-radius: 8px;
        padding: 15px;
        border: 1px solid #2E3440;
        text-align: center;
    }
    .kpi-title {
        font-size: 0.85rem;
        color: #A0AEC0;
        text-transform: uppercase;
        font-weight: 600;
        margin-bottom: 5px;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #F8FAFC;
    }
    .badge-hw {
        background-color: #2b4c7e;
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-bw {
        background-color: #9c413e;
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-rating {
        background-color: #2E7D32;
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Directory Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, 'data', 'processed')


@st.cache_data
def load_all_data():
    """Load preprocessed recommender artifacts and Power BI tabular data."""
    movies_path = os.path.join(MODELS_DIR, 'movies_list.pkl')
    matches_path = os.path.join(MODELS_DIR, 'top_matches.pkl')
    pbi_path = os.path.join(PROCESSED_DATA_DIR, 'movies_powerbi.csv')

    with open(movies_path, 'rb') as f:
        movies_df = pickle.load(f)

    with open(matches_path, 'rb') as f:
        top_matches = pickle.load(f)

    pbi_df = pd.read_csv(pbi_path)

    return movies_df, top_matches, pbi_df


movies_df, top_matches, pbi_df = load_all_data()

# Genre fallback images
GENRE_FALLBACK_IMAGES = {
    'Action': 'https://images.unsplash.com/photo-1534447677768-be436bb09401?w=400&q=80',
    'Drama': 'https://images.unsplash.com/photo-1485846234645-a62644f84728?w=400&q=80',
    'Comedy': 'https://images.unsplash.com/photo-1514306191717-452ec28c7814?w=400&q=80',
    'Romance': 'https://images.unsplash.com/photo-1518895949257-7621c3c786d7?w=400&q=80',
    'Thriller': 'https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=400&q=80',
    'Horror': 'https://images.unsplash.com/photo-1509248961158-e54f6934749c?w=400&q=80',
    'Science Fiction': 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400&q=80',
    'Default': 'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=400&q=80'
}


def get_poster_url(row):
    """Retrieve poster: uses Wikimedia link for Bollywood, TMDB API (or fallback) for Hollywood."""
    existing_url = str(row.get('poster_url', '')).strip()
    if existing_url.startswith('http'):
        return existing_url

    tmdb_id = row.get('tmdb_id')
    if pd.notna(tmdb_id) and int(tmdb_id) > 0:
        try:
            url = f"https://api.themoviedb.org/3/movie/{int(tmdb_id)}?api_key=8265bd1679663a7ea12ac168da84d2e8"
            r = requests.get(url, timeout=1.2)
            if r.status_code == 200:
                p_path = r.json().get('poster_path')
                if p_path:
                    return f"https://image.tmdb.org/t/p/w500{p_path}"
        except Exception:
            pass

    genre = str(row.get('primary_genre', 'Default'))
    return GENRE_FALLBACK_IMAGES.get(genre, GENRE_FALLBACK_IMAGES['Default'])


# ==================== SIDEBAR ====================
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=500&q=80", use_container_width=True)
    st.title("🎬 CineMatch Navigation")
    
    app_mode = st.radio(
        "Choose View:",
        ["🎯 Movie Recommender", "📊 Analytics Dashboard"],
        index=0
    )

    st.markdown("---")
    st.markdown("### 📌 Recommender Filters")
    industry_filter = st.selectbox(
        "Industry Preference:",
        ["All (Hollywood + Bollywood)", "Only Hollywood", "Only Bollywood"],
        index=0
    )
    num_recommendations = st.slider("Number of Recommendations:", min_value=3, max_value=12, value=6)
    min_rating = st.slider("Minimum Rating Threshold:", min_value=0.0, max_value=9.0, value=5.0, step=0.5)

    st.markdown("---")
    st.markdown("**Catalog Overview:**")
    st.caption(f"• Total Movies: **{len(movies_df):,}**")
    st.caption(f"• Hollywood: **{(movies_df['industry'] == 'Hollywood').sum():,}**")
    st.caption(f"• Bollywood: **{(movies_df['industry'] == 'Bollywood').sum():,}**")


# ==================== VIEW 1: MOVIE RECOMMENDER ====================
if app_mode == "🎯 Movie Recommender":
    st.markdown('<div class="main-title">🎬 CineMatch: Movie Recommendation Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Content-Based Machine Learning Recommender trained on 9,000+ Hollywood and Bollywood titles.</div>', unsafe_allow_html=True)

    movie_titles = movies_df['title'].tolist()
    default_idx = movie_titles.index("Inception") if "Inception" in movie_titles else 0

    col_select, col_btn = st.columns([4, 1])
    with col_select:
        selected_movie_title = st.selectbox(
            "Type or select a movie:",
            movie_titles,
            index=default_idx
        )

    with col_btn:
        st.write("")
        st.write("")
        st.button("🚀 Recommend", type="primary", use_container_width=True)

    # Spotlight Card
    selected_idx = movies_df[movies_df['title'] == selected_movie_title].index[0]
    selected_movie = movies_df.iloc[selected_idx]

    with st.expander("📌 Selected Movie Spotlight", expanded=True):
        col_img, col_info = st.columns([1, 4])
        with col_img:
            sel_poster = get_poster_url(selected_movie)
            st.image(sel_poster, use_container_width=True)
        with col_info:
            ind_badge = '<span class="badge-hw">Hollywood</span>' if selected_movie['industry'] == 'Hollywood' else '<span class="badge-bw">Bollywood</span>'
            rating_badge = f'<span class="badge-rating">⭐ {selected_movie["rating"]}/10</span>'
            
            st.markdown(f"### {selected_movie['title']} ({selected_movie['release_year']}) {ind_badge} {rating_badge}", unsafe_allow_html=True)
            st.markdown(f"**Genre:** {selected_movie['primary_genre']} | **Director:** {selected_movie['director']}")
            st.markdown(f"**Top Cast:** {selected_movie['top_cast']}")
            if selected_movie['overview']:
                st.markdown(f"_{selected_movie['overview']}_")

    # Recommendations Grid
    st.markdown("### 🍿 Top Recommended Matches")

    match_data = top_matches.get(selected_idx, {'indices': [], 'scores': []})
    candidate_indices = match_data['indices']
    candidate_scores = match_data['scores']

    filtered_recs = []
    for idx, score in zip(candidate_indices, candidate_scores):
        cand = movies_df.iloc[idx]
        if industry_filter == "Only Hollywood" and cand['industry'] != 'Hollywood':
            continue
        if industry_filter == "Only Bollywood" and cand['industry'] != 'Bollywood':
            continue
        if cand['rating'] < min_rating:
            continue
        filtered_recs.append((cand, score))
        if len(filtered_recs) == num_recommendations:
            break

    if not filtered_recs:
        st.warning("No movies matched the current filters! Try lowering the minimum rating threshold.")
    else:
        cols_per_row = 3
        for i in range(0, len(filtered_recs), cols_per_row):
            cols = st.columns(cols_per_row)
            for j in range(cols_per_row):
                if i + j < len(filtered_recs):
                    cand_movie, sim_score = filtered_recs[i + j]
                    with cols[j]:
                        with st.container():
                            p_url = get_poster_url(cand_movie)
                            st.image(p_url, use_container_width=True)
                            
                            ind_badge = "🔵 Hollywood" if cand_movie['industry'] == 'Hollywood' else "🔴 Bollywood"
                            st.markdown(f"**{cand_movie['title']}** ({int(float(cand_movie['release_year'])) if pd.notna(cand_movie['release_year']) else 'N/A'})")
                            st.caption(f"{ind_badge} | ⭐ {cand_movie['rating']} | Match: **{int(sim_score*100)}%**")
                            st.write(f"🎭 **Cast:** {cand_movie['top_cast']}")
                            if cand_movie['overview']:
                                short_desc = cand_movie['overview'][:110] + "..." if len(cand_movie['overview']) > 110 else cand_movie['overview']
                                st.caption(f"_{short_desc}_")
                            st.markdown("---")


# ==================== VIEW 2: EXECUTIVE ANALYTICS DASHBOARD ====================
elif app_mode == "📊 Analytics Dashboard":
    st.markdown('<div class="main-title">📊 Executive Movie Industry Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Interactive Box Office, ROI, and Industry Trend Analytics (Simulating Power BI Experience).</div>', unsafe_allow_html=True)

    # Dashboard Slicers / Interactive Filters
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        dash_industry = st.selectbox("Filter Industry:", ["All Industries", "Hollywood", "Bollywood"])
    with col_f2:
        decades_list = ["All Decades", "2010s", "2000s", "1990s", "1980s", "1970s", "Pre-1970s"]
        dash_decade = st.selectbox("Filter Decade:", decades_list)
    with col_f3:
        all_genres = ["All Genres"] + sorted(pbi_df['primary_genre'].dropna().unique().tolist())
        dash_genre = st.selectbox("Filter Primary Genre:", all_genres)

    # Filter DataFrame
    filtered_df = pbi_df.copy()
    if dash_industry != "All Industries":
        filtered_df = filtered_df[filtered_df['industry'] == dash_industry]
    if dash_decade != "All Decades":
        filtered_df = filtered_df[filtered_df['decade'] == dash_decade]
    if dash_genre != "All Genres":
        filtered_df = filtered_df[filtered_df['primary_genre'] == dash_genre]

    # Financial slice
    fin_df = filtered_df[filtered_df['has_financial_data']].copy()

    # KPI Summary Cards
    st.markdown("### 📈 Key Performance Indicators (KPIs)")
    k1, k2, k3, k4, k5 = st.columns(5)

    tot_movies = len(filtered_df)
    tot_revenue = fin_df['revenue_usd'].sum() if not fin_df.empty else 0
    tot_profit = fin_df['profit_usd'].sum() if not fin_df.empty else 0
    profit_margin = (tot_profit / tot_revenue * 100) if tot_revenue > 0 else 0
    avg_rating = filtered_df[filtered_df['rating'] > 0]['rating'].mean() if not filtered_df.empty else 0

    with k1:
        st.markdown(f'<div class="kpi-box"><div class="kpi-title">Total Movies</div><div class="kpi-value">{tot_movies:,}</div></div>', unsafe_allow_html=True)
    with k2:
        rev_str = f"${tot_revenue / 1e9:.1f}B" if tot_revenue >= 1e9 else f"${tot_revenue / 1e6:.1f}M"
        st.markdown(f'<div class="kpi-box"><div class="kpi-title">Box Office Revenue</div><div class="kpi-value">{rev_str}</div></div>', unsafe_allow_html=True)
    with k3:
        prof_str = f"${tot_profit / 1e9:.1f}B" if tot_profit >= 1e9 else f"${tot_profit / 1e6:.1f}M"
        st.markdown(f'<div class="kpi-box"><div class="kpi-title">Net Profit</div><div class="kpi-value">{prof_str}</div></div>', unsafe_allow_html=True)
    with k4:
        st.markdown(f'<div class="kpi-box"><div class="kpi-title">Profit Margin %</div><div class="kpi-value">{profit_margin:.1f}%</div></div>', unsafe_allow_html=True)
    with k5:
        st.markdown(f'<div class="kpi-box"><div class="kpi-title">Average Rating</div><div class="kpi-value">⭐ {avg_rating:.2f}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 1: Charts
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.markdown("#### 💰 Production Budget vs. Box Office Revenue")
        if not fin_df.empty:
            scatter_data = fin_df[['title', 'budget_usd', 'revenue_usd', 'primary_genre']].copy()
            scatter_data['Budget (Million $)'] = round(scatter_data['budget_usd'] / 1e6, 1)
            scatter_data['Revenue (Million $)'] = round(scatter_data['revenue_usd'] / 1e6, 1)
            
            scatter_chart = alt.Chart(scatter_data.head(500)).mark_circle(size=70).encode(
                x='Budget (Million $):Q',
                y='Revenue (Million $):Q',
                color='primary_genre:N',
                tooltip=['title', 'Budget (Million $)', 'Revenue (Million $)', 'primary_genre']
            ).properties(height=350).interactive()
            st.altair_chart(scatter_chart, use_container_width=True)
        else:
            st.info("No financial data available for this filter combination.")

    with col_c2:
        st.markdown("#### 🏆 Top 10 Highest Grossing Blockbusters")
        if not fin_df.empty:
            top_grossing = fin_df.sort_values(by='revenue_usd', ascending=False).head(10)[['title', 'revenue_usd']].copy()
            top_grossing['Revenue (Million $)'] = round(top_grossing['revenue_usd'] / 1e6, 1)
            
            bar_chart = alt.Chart(top_grossing).mark_bar(color='#FF4B4B').encode(
                x=alt.X('Revenue (Million $):Q', title='Box Office Revenue ($M)'),
                y=alt.Y('title:N', sort='-x', title='Movie Title'),
                tooltip=['title', 'Revenue (Million $)']
            ).properties(height=350)
            st.altair_chart(bar_chart, use_container_width=True)
        else:
            st.info("No financial data available.")

    # Row 2: Charts
    col_c3, col_c4 = st.columns(2)
    with col_c3:
        st.markdown("#### 📅 Movie Releases & Rating Across Decades")
        decade_stats = filtered_df.groupby('decade').agg(
            Movie_Count=('movie_id', 'count'),
            Avg_Rating=('rating', lambda x: round(x[x > 0].mean(), 2) if len(x[x > 0]) > 0 else 0)
        ).reset_index()
        # Sort decades chronologically
        dec_order = ["Pre-1970s", "1970s", "1980s", "1990s", "2000s", "2010s", "2020s"]
        decade_stats['sort_order'] = decade_stats['decade'].apply(lambda d: dec_order.index(d) if d in dec_order else 99)
        decade_stats = decade_stats.sort_values('sort_order')

        dec_chart = alt.Chart(decade_stats).mark_bar(color='#2b4c7e').encode(
            x=alt.X('decade:N', sort=dec_order, title='Decade'),
            y=alt.Y('Movie_Count:Q', title='Number of Releases'),
            tooltip=['decade', 'Movie_Count', 'Avg_Rating']
        ).properties(height=320)
        st.altair_chart(dec_chart, use_container_width=True)

    with col_c4:
        st.markdown("#### 🎭 Box Office Revenue by Genre ($ Million)")
        if not fin_df.empty:
            genre_rev = fin_df.groupby('primary_genre')['revenue_usd'].sum().reset_index()
            genre_rev['Revenue ($M)'] = round(genre_rev['revenue_usd'] / 1e6, 1)
            genre_rev = genre_rev.sort_values(by='Revenue ($M)', ascending=False).head(10)

            genre_chart = alt.Chart(genre_rev).mark_bar(color='#3e8e41').encode(
                x=alt.X('Revenue ($M):Q', title='Gross Revenue ($M)'),
                y=alt.Y('primary_genre:N', sort='-x', title='Genre'),
                tooltip=['primary_genre', 'Revenue ($M)']
            ).properties(height=320)
            st.altair_chart(genre_chart, use_container_width=True)
        else:
            st.info("No financial data available.")

    # Row 3: Top Rated Movies Explorer
    st.markdown("#### ⭐ Top 10 All-Time Highest Rated Movies (Minimum 100 Votes)")
    qualified_rated = filtered_df[(filtered_df['votes'] >= 100) & (filtered_df['rating'] > 0)].sort_values(by='rating', ascending=False).head(10)
    st.dataframe(
        qualified_rated[['title', 'industry', 'release_year', 'primary_genre', 'director', 'rating', 'votes']].reset_index(drop=True),
        use_container_width=True
    )



# Footer
st.markdown("---")
st.caption("CineMatch Portfolio Project | Built with Python • Scikit-Learn • Streamlit • Power BI • Pandas")
