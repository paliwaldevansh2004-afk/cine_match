# 🎬 CineMatch: Hollywood & Bollywood Movie Recommender + Power BI Dashboard

An end-to-end Machine Learning and Business Intelligence project built with **Python**, **Scikit-Learn**, **Streamlit**, and **Power BI**. 

Designed as a production-ready, fresher-friendly portfolio project showcasing **ETL pipelines**, **Content-Based NLP Recommendation**, and **Executive Financial Analytics**.

---

## 📌 Project Highlights
* **Dual-Industry Movie Catalog:** 9,091 total films (4,803 Hollywood + 4,288 Bollywood).
* **Content-Based Filtering:** Recommends movies based on plot summaries, genres, director, and top cast members using `TfidfVectorizer` (TF-IDF) and `Cosine Similarity`.
* **Sub-Millisecond Queries:** Optimized with offline top-N precomputations (reducing memory overhead by 98%).
* **Interactive Web Application:** Built with **Streamlit**, featuring instant movie search, poster cards, industry/rating filters, and EDA metrics.
* **Executive Power BI Dashboard:** Clean data pipeline feeding into Power BI Desktop for Box Office revenue, ROI, and genre analytics.

---

## 📁 Project Structure

```
movie_recommender_system/
├── data/
│   ├── raw/                       # Original downloaded CSVs
│   │   ├── tmdb_5000_movies.csv
│   │   ├── tmdb_5000_credits.csv
│   │   ├── bollywood_full.csv
│   │   ├── bollywood_crew.csv
│   │   └── bollywood_crew_data.csv
│   └── processed/                 # Cleaned datasets ready for use
│       ├── movies_powerbi.csv     # 18-column tabular data for Power BI
│       └── movies_recommender.csv # NLP-ready tags and metadata
├── models/                        # Serialized artifacts
│   ├── movies_list.pkl            # Clean movie catalog for UI
│   ├── top_matches.pkl            # Precomputed Top-30 neighbors per movie
│   └── cv_model.pkl               # Fitted CountVectorizer model
├── src/
│   ├── data_preprocessing.py      # ETL pipeline (unifies schemas & feature engineering)
│   └── build_model.py             # NLP vectorization & neighbor precomputation
├── app.py                         # Streamlit interactive web application
├── POWERBI_GUIDE.md               # Step-by-step dashboard setup guide + DAX measures
├── INTERVIEW_PREP.md              # Complete interview questions & STAR-method answers
├── requirements.txt               # Python package dependencies
└── README.md                      # Project documentation
```

---

## 🚀 How to Run the Project

### 1. Setup Environment & Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. (Optional) Run the ETL Pipeline & Retrain Model
```bash
# Clean datasets and create Power BI & recommender CSVs:
python src/data_preprocessing.py

# Build NLP model and precompute similarity matches:
python src/build_model.py
```

### 3. Launch the Streamlit Web Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

### 4. Build the Power BI Dashboard
1. Open **Power BI Desktop**.
2. Load `data/processed/movies_powerbi.csv`.
3. Follow the visual layout and copy-paste DAX formulas from `POWERBI_GUIDE.md`.

---

## 🎯 Key Learnings & Fresher Presentation
Check out [`INTERVIEW_PREP.md`](POWERBI_GUIDE.md) for in-depth answers to top technical and behavioral interview questions regarding this project.
