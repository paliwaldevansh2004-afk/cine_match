"""
Script to generate a self-contained, interactive Executive BI Dashboard HTML file.
Zero dependencies needed to view - just double-click to open in any browser!
"""

import os
import json
import pandas as pd

BASE_DIR = r"C:\Users\paliw\OneDrive\Desktop\movie_recommender_system"
csv_path = os.path.join(BASE_DIR, "data", "processed", "movies_powerbi.csv")
df = pd.read_csv(csv_path)

# Overall KPIs
total_movies = len(df)
fin = df[df['has_financial_data']].copy()
total_rev = fin['revenue_usd'].sum()
total_budget = fin['budget_usd'].sum()
total_profit = fin['profit_usd'].sum()
profit_margin = round((total_profit / total_rev) * 100, 1)
avg_rating = round(df[df['rating'] > 0]['rating'].mean(), 2)

# Top 10 Grossing
top10 = fin.sort_values(by='revenue_usd', ascending=False).head(10)
top10_labels = top10['title'].tolist()
top10_rev = [round(x / 1e6, 1) for x in top10['revenue_usd']]
top10_budget = [round(x / 1e6, 1) for x in top10['budget_usd']]

# Genre Breakdown
genre_rev = fin.groupby('primary_genre')['revenue_usd'].sum().sort_values(ascending=False).head(8)
genre_labels = genre_rev.index.tolist()
genre_values = [round(x / 1e6, 1) for x in genre_rev.values]

# Decade Trend
dec_order = ["Pre-1970s", "1970s", "1980s", "1990s", "2000s", "2010s"]
dec_counts = df['decade'].value_counts()
decade_vals = [int(dec_counts.get(d, 0)) for d in dec_order]

# Top Rated Table
top_rated = df[(df['votes'] >= 100) & (df['rating'] > 0)].sort_values(by='rating', ascending=False).head(10)
table_rows = []
for _, r in top_rated.iterrows():
    table_rows.append({
        'title': r['title'],
        'industry': r['industry'],
        'year': int(r['release_year']) if pd.notna(r['release_year']) else 'N/A',
        'genre': r['primary_genre'],
        'director': r['director'],
        'rating': r['rating'],
        'votes': f"{int(r['votes']):,}"
    })

# Scatter top 40
scatter_sample = fin.sort_values(by='revenue_usd', ascending=False).head(40)
scatter_points = []
for _, r in scatter_sample.iterrows():
    scatter_points.append({
        'x': round(r['budget_usd'] / 1e6, 1),
        'y': round(r['revenue_usd'] / 1e6, 1),
        'title': r['title']
    })

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CineMatch - Power BI Executive Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        body {{ background-color: #0F172A; color: #F8FAFC; padding: 25px; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; border-bottom: 1px solid #1E293B; padding-bottom: 15px; }}
        .title-box h1 {{ font-size: 26px; font-weight: 800; background: linear-gradient(90deg, #F59E0B, #EF4444); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .title-box p {{ font-size: 13px; color: #94A3B8; margin-top: 4px; }}
        .badge {{ background: #1E293B; color: #38BDF8; padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 600; border: 1px solid #334155; }}
        
        .kpi-grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 15px; margin-bottom: 25px; }}
        .kpi-card {{ background: #1E293B; border-radius: 12px; padding: 18px; border: 1px solid #334155; text-align: center; }}
        .kpi-title {{ font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: #94A3B8; font-weight: 700; margin-bottom: 6px; }}
        .kpi-value {{ font-size: 26px; font-weight: 800; color: #F8FAFC; }}
        .kpi-sub {{ font-size: 11px; color: #10B981; margin-top: 4px; }}

        .charts-grid {{ display: grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-bottom: 25px; }}
        .chart-card {{ background: #1E293B; border-radius: 12px; padding: 20px; border: 1px solid #334155; }}
        .chart-header {{ font-size: 15px; font-weight: 700; margin-bottom: 15px; color: #E2E8F0; display: flex; justify-content: space-between; align-items: center; }}

        .bottom-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px; }}
        
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }}
        th {{ background: #0F172A; color: #94A3B8; text-align: left; padding: 10px; font-weight: 600; }}
        td {{ padding: 10px; border-bottom: 1px solid #334155; color: #CBD5E1; }}
        tr:hover td {{ background: #273549; }}
        .rating-badge {{ background: #065F46; color: #6EE7B7; padding: 3px 8px; border-radius: 6px; font-weight: 700; }}
    </style>
</head>
<body>

    <div class="header">
        <div class="title-box">
            <h1>🎬 CineMatch: Executive Movie Industry Dashboard</h1>
            <p>Hollywood & Bollywood Box Office Financials, ROI Multipliers & Global Industry Trends (9,091 Titles)</p>
        </div>
        <div class="badge">● Live Ready Dashboard</div>
    </div>

    <!-- 5 KPI Cards -->
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-title">Total Catalog Movies</div>
            <div class="kpi-value">{total_movies:,}</div>
            <div class="kpi-sub">4,803 HW • 4,288 BW</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Global Box Office Gross</div>
            <div class="kpi-value">${total_rev / 1e9:.1f}B</div>
            <div class="kpi-sub">Verified Box Office</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Net Studio Profit</div>
            <div class="kpi-value">${total_profit / 1e9:.1f}B</div>
            <div class="kpi-sub">Revenue - Budget</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Profit Margin %</div>
            <div class="kpi-value">{profit_margin}%</div>
            <div class="kpi-sub">Aggregate Industry ROI</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Audience Avg Rating</div>
            <div class="kpi-value">⭐ {avg_rating}</div>
            <div class="kpi-sub">Across All Decades</div>
        </div>
    </div>

    <!-- Charts Row 1 -->
    <div class="charts-grid">
        <div class="chart-card">
            <div class="chart-header">
                <span>🏆 Top 10 Highest Grossing Blockbusters (Box Office vs Budget in $ Million)</span>
            </div>
            <div style="height: 320px;">
                <canvas id="barChart"></canvas>
            </div>
        </div>
        <div class="chart-card">
            <div class="chart-header">
                <span>🎭 Box Office Revenue by Genre</span>
            </div>
            <div style="height: 320px;">
                <canvas id="donutChart"></canvas>
            </div>
        </div>
    </div>

    <!-- Charts Row 2 -->
    <div class="bottom-grid">
        <div class="chart-card">
            <div class="chart-header">
                <span>📅 Industry Evolution: Releases Across Decades</span>
            </div>
            <div style="height: 280px;">
                <canvas id="decadeChart"></canvas>
            </div>
        </div>
        <div class="chart-card">
            <div class="chart-header">
                <span>💰 Production Budget vs Box Office Revenue ($M)</span>
            </div>
            <div style="height: 280px;">
                <canvas id="scatterChart"></canvas>
            </div>
        </div>
    </div>

    <!-- Data Table -->
    <div class="chart-card">
        <div class="chart-header">
            <span>⭐ All-Time Highest Rated Titles (Minimum 100 Verified Votes)</span>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Title</th>
                    <th>Industry</th>
                    <th>Year</th>
                    <th>Primary Genre</th>
                    <th>Director</th>
                    <th>Votes</th>
                    <th>IMDb / TMDB Score</th>
                </tr>
            </thead>
            <tbody>
"""

for row in table_rows:
    html_content += f"""
                <tr>
                    <td><strong>{row['title']}</strong></td>
                    <td>{row['industry']}</td>
                    <td>{row['year']}</td>
                    <td>{row['genre']}</td>
                    <td>{row['director']}</td>
                    <td>{row['votes']}</td>
                    <td><span class="rating-badge">⭐ {row['rating']}</span></td>
                </tr>
    """

html_content += f"""
            </tbody>
        </table>
    </div>

    <script>
        // 1. Top 10 Horizontal Bar
        new Chart(document.getElementById('barChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(top10_labels)},
                datasets: [
                    {{
                        label: 'Gross Revenue ($M)',
                        data: {json.dumps(top10_rev)},
                        backgroundColor: '#EF4444'
                    }},
                    {{
                        label: 'Budget ($M)',
                        data: {json.dumps(top10_budget)},
                        backgroundColor: '#3B82F6'
                    }}
                ]
            }},
            options: {{
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ labels: {{ color: '#94A3B8' }} }} }},
                scales: {{
                    x: {{ ticks: {{ color: '#94A3B8' }}, grid: {{ color: '#334155' }} }},
                    y: {{ ticks: {{ color: '#E2E8F0', font: {{ weight: 'bold' }} }}, grid: {{ display: false }} }}
                }}
            }}
        }});

        // 2. Genre Donut
        new Chart(document.getElementById('donutChart'), {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(genre_labels)},
                datasets: [{{
                    data: {json.dumps(genre_values)},
                    backgroundColor: ['#F59E0B', '#EF4444', '#10B981', '#3B82F6', '#8B5CF6', '#EC4899', '#06B6D4', '#64748B']
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ position: 'right', labels: {{ color: '#CBD5E1', boxWidth: 12 }} }} }}
            }}
        }});

        // 3. Decade Chart
        new Chart(document.getElementById('decadeChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(dec_order)},
                datasets: [{{
                    label: 'Movie Releases',
                    data: {json.dumps(decade_vals)},
                    backgroundColor: '#38BDF8',
                    borderRadius: 6
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ ticks: {{ color: '#94A3B8' }}, grid: {{ display: false }} }},
                    y: {{ ticks: {{ color: '#94A3B8' }}, grid: {{ color: '#334155' }} }}
                }}
            }}
        }});

        // 4. Scatter Chart
        new Chart(document.getElementById('scatterChart'), {{
            type: 'scatter',
            data: {{
                datasets: [{{
                    label: 'Top Movies',
                    data: {json.dumps(scatter_points)},
                    backgroundColor: '#10B981',
                    borderColor: '#059669',
                    pointRadius: 6,
                    pointHoverRadius: 9
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    tooltip: {{
                        callbacks: {{
                            label: function(ctx) {{
                                var pt = ctx.raw;
                                return pt.title + ' (Budget: $' + pt.x + 'M, Revenue: $' + pt.y + 'M)';
                            }}
                        }}
                    }},
                    legend: {{ display: false }}
                }},
                scales: {{
                    x: {{ title: {{ display: true, text: 'Budget ($M)', color: '#94A3B8' }}, ticks: {{ color: '#94A3B8' }}, grid: {{ color: '#334155' }} }},
                    y: {{ title: {{ display: true, text: 'Revenue ($M)', color: '#94A3B8' }}, ticks: {{ color: '#94A3B8' }}, grid: {{ color: '#334155' }} }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

output_path = os.path.join(BASE_DIR, "CineMatch_Executive_Dashboard.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"[SUCCESS] Standalone Dashboard created at: {output_path}")
print(f"File size: {os.path.getsize(output_path)} bytes")
