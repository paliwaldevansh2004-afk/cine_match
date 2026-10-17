# 🎯 Fresher Interview Q&A Guide: Movie Recommendation System & Power BI Dashboard

This guide prepares you to explain every aspect of this project during technical and managerial interviews. Each answer is structured using the **STAR Method (Situation, Task, Action, Result)**.

---

### Q1: Can you walk me through this project from end to end?
**Model Answer:**
> *"I built an end-to-end Movie Recommendation System and companion Business Intelligence Dashboard using Python, Scikit-Learn, Streamlit, and Power BI.*
> 
> *The goal was twofold: first, build an interactive NLP-based content recommendation engine capable of suggesting both Hollywood and Bollywood films. Second, create an executive Power BI dashboard to evaluate box office performance, ROI, genre trends, and industry comparisons across 9,000+ films.*
> 
> *I integrated two datasets: TMDB 5000 and TIMDB (The Indian Movie Database). I cleaned nested JSON fields, mapped directors from crew tables, engineered financial metrics (Profit and ROI), and combined metadata into text tags. Using `TfidfVectorizer` (TF-IDF) and `Cosine Similarity`, I precomputed top similarity rankings to ensure sub-millisecond query responses in Streamlit. Finally, I exported clean tabular data into Power BI, designed custom DAX measures, and visualized financial and content patterns."*

---

### Q2: Why did you choose Content-Based Filtering instead of Collaborative Filtering?
**Model Answer:**
> *"I opted for Content-Based Filtering for two primary reasons:*
> 1. **Cold Start Problem:** Collaborative Filtering requires extensive historical user rating matrices. For a new application without user login histories, it cannot recommend items to new users. Content-Based filtering recommends immediately based purely on item metadata (director, cast, genres, overview).
> 2. **Cross-Industry Discovery:** It allows users to discover movies across different industries based on theme or style (e.g. recommending high-stakes military action like *Pukar* or *Deewaar* to someone who liked *Uri* or *One Man's Hero*).*
> 
> *However, as a future enhancement, I have designed the schema so it can be extended into a Hybrid Recommender once user rating logs are collected."*

---

### Q3: Why did you use Cosine Similarity instead of Euclidean Distance?
**Model Answer:**
> *"Cosine Similarity measures the cosine of the angle between two vectors rather than their geometric distance in space:*
> $$\text{Cosine Similarity}(\vec{A}, \vec{B}) = \frac{\vec{A} \cdot \vec{B}}{\|\vec{A}\| \|\vec{B}\|}$$
> *In text vectorization (NLP), document length varies widely. A movie with a 200-word plot synopsis would have a large Euclidean distance from a movie with a 40-word synopsis, even if their genres, cast, and themes are identical.*
> *Cosine Similarity is length-invariant—it focuses strictly on the orientation/direction of the vectors, ensuring similarity is determined by shared themes rather than description length."*

---

### Q4: Why is TF-IDF better than CountVectorizer in this project?
**Model Answer:**
> *"CountVectorizer only looks at raw term frequencies. In movie synopses, generic terms like 'life', 'story', and 'family' appear very frequently across hundreds of movies, inflating false similarity scores.*
> *TF-IDF (Term Frequency - Inverse Document Frequency) down-weights ubiquitous terms and gives higher mathematical importance to distinctive keywords (e.g., 'superhero', 'espionage', 'time travel') and unique talent names (e.g., 'christophernolan', 'rajkumarhirani'), resulting in vastly superior recommendation precision."*

---

### Q5: How did you optimize Streamlit performance and memory consumption?
**Model Answer:**
> *"A naive implementation would calculate a full $9,091 \times 9,091$ cosine similarity matrix at runtime or load a 600+ MB matrix into memory. In production, this causes high memory consumption and latency.*
> 
> *Instead, I optimized the architecture:*
> 1. **Offline Precomputation:** During model training, I precomputed the Top 30 similar neighbors and their scores for each film.
> 2. **Serialized Lookups:** I stored these in a compressed dictionary (`top_matches.pkl`), reducing memory from 600 MB down to ~7 MB (a 98% reduction).
> 3. **Streamlit Caching:** I used `@st.cache_data` so artifacts are loaded into memory once and reused across user sessions, resulting in instant search and recommendation response times."*

---

### Q6: What DAX measures did you build in Power BI, and what key insights did you find?
**Model Answer:**
> *"In Power BI, I wrote several DAX measures:*
> * `Total Box Office Revenue = SUM(movies_powerbi[revenue_usd])`
> * `Total Net Profit = [Total Revenue] - [Total Budget]`
> * `Profit Margin % = DIVIDE([Total Profit], [Total Revenue], 0) * 100`
> * `Average Rating = AVERAGE(movies_powerbi[rating])`
> 
> **Key Business Insights Uncovered:**
> 1. **Genre Profitability:** Action and Adventure make up the majority of box office gross, but Animation and Horror deliver significantly higher Profit Margins relative to production budget.
> 2. **Decade Boom:** The 2000s and 2010s saw an exponential increase in total releases, yet the average audience rating remained stable between 6.2 and 6.6.
> 3. **Industry Nuance:** Bollywood produces a much higher proportion of Drama and Romance titles, whereas Hollywood dominates Sci-Fi and Animation."*
