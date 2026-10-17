# 📊 Power BI Dashboard Guide: Movie Industry Analytics

Welcome to the Power BI companion dashboard guide for the **CineMatch** project. This document provides step-by-step instructions on importing the cleaned dataset, writing DAX measures, and creating high-impact visual reports.

---

## 1. Dataset Overview

* **File Location:** `data/processed/movies_powerbi.csv`
* **Total Records:** 9,091 movies (4,803 Hollywood + 4,288 Bollywood)
* **Key Columns:**
  * Categorical: `title`, `industry`, `decade`, `primary_genre`, `genres`, `director`, `top_cast`, `rating_category`
  * Numerical: `release_year`, `rating`, `votes`, `runtime_mins`, `budget_usd`, `revenue_usd`, `profit_usd`, `roi_percentage`
  * Flags: `has_financial_data` (TRUE/FALSE)

---

## 2. Importing Data into Power BI Desktop

1. Open **Power BI Desktop**.
2. Click on **Get Data** $\rightarrow$ **Text/CSV**.
3. Select `data/processed/movies_powerbi.csv`.
4. In the preview window, click **Transform Data** (Power Query):
   * Verify Data Types:
     * `release_year` $\rightarrow$ Whole Number
     * `rating` $\rightarrow$ Decimal Number
     * `budget_usd`, `revenue_usd`, `profit_usd` $\rightarrow$ Currency or Decimal Number
     * `has_financial_data` $\rightarrow$ True/False
5. Click **Close & Apply**.

---

## 3. Core DAX Measures (Copy & Paste)

### 🔹 Volume & Rating Measures
```dax
Total Movies = 
COUNTROWS(movies_powerbi)
```

```dax
Average Rating = 
AVERAGE(movies_powerbi[rating])
```

```dax
Total Votes = 
SUM(movies_powerbi[votes])
```

```dax
Classic Movies Count = 
CALCULATE(
    COUNTROWS(movies_powerbi), 
    movies_powerbi[rating] >= 8.0
)
```

### 🔹 Financial Measures (Box Office & Profitability)
```dax
Total Box Office Revenue = 
SUM(movies_powerbi[revenue_usd])
```

```dax
Total Production Budget = 
SUM(movies_powerbi[budget_usd])
```

```dax
Total Net Profit = 
[Total Box Office Revenue] - [Total Production Budget]
```

```dax
Profit Margin % = 
DIVIDE([Total Net Profit], [Total Box Office Revenue], 0) * 100
```

```dax
Average ROI % = 
AVERAGE(movies_powerbi[roi_percentage])
```

```dax
Profitable Movies Count = 
CALCULATE(
    COUNTROWS(movies_powerbi), 
    movies_powerbi[profit_usd] > 0
)
```

---

## 4. Dashboard Layout & Visuals Structure

### 📄 Page 1: Executive Overview & Box Office Financials
* **KPI Cards:** Total Movies (`9,091`), Total Revenue (`$365B+`), Total Profit (`$210B+`), Profit Margin % (`57.5%`), Avg Rating (`⭐ 6.4/10`).
* **Visual 1 (Scatter Plot):** Budget vs Revenue (Color by Genre, Details by Title).
* **Visual 2 (Bar Chart):** Top 10 Most Profitable Movies.
* **Visual 3 (Treemap / Donut):** Revenue Share by Primary Genre.

### 📄 Page 2: Content Trends, Decades & Talent Analysis
* **Visual 1 (Line & Column Chart):** Movie Releases & Average Rating Across Decades.
* **Visual 2 (Bar Chart):** Top Directors by Average Rating (Minimum 3 movies).
* **Visual 3 (Clustered Column Chart):** Industry Comparison: Hollywood vs. Bollywood Genre distribution.
