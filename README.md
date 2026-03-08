---
title: DataMind Pro
emoji: ⚡
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
app_port: 7860
---
# ⚡ DataMind Pro — AI-Powered Data Analysis Platform

> A full-stack data analyst in your browser. Upload any dataset and get professional EDA, statistical analysis, ML predictions, AI-generated insights, and actionable recommendations — all in one place.

---

## 💡 The Problem I Wanted to Solve

Every time I had to analyze a dataset, I found myself doing the same repetitive things — cleaning data in pandas, writing matplotlib code for charts, manually identifying patterns, writing up findings. It took hours just to get to the "interesting part."

I wanted something that could do all of that automatically, the way a senior data analyst would — not just show some basic charts, but actually follow the real workflow: define the problem, collect and validate data, clean it, analyze patterns, communicate findings clearly, and recommend what to do next.

That's what DataMind Pro is.

---

## 🎯 What It Does

DataMind Pro follows the complete 6-step data analysis workflow:

```
Step 1 → Ask the Right Question    (goal definition wizard)
Step 2 → Collect Relevant Data     (file upload + DB connect)
Step 3 → Clean & Transform Data    (8 transformation operations)
Step 4 → Analyze Patterns          (EDA + charts)
Step 5 → Communicate Insights      (AI executive summary + data story)
Step 6 → Recommend Actions         (prioritized action items)
```

Because insight without action = useless.

---

## ✨ Features

### 📊 Analysis Engine
- Full EDA — descriptive stats, distributions, outlier detection (IQR), normality tests (Shapiro-Wilk)
- Correlation analysis — Pearson, Spearman, Kendall matrices with strong-pair detection
- PCA summary — explained variance, component loadings
- Data quality scoring (0–100) with issue detection and fix recommendations
- ANOVA group analysis — categorical vs numeric significance testing

### 📈 Charts & Visualizations
- Distribution dashboards (KDE + histogram) — Matplotlib
- Box plots, violin plots, Q-Q plots — Seaborn
- Correlation heatmaps — Seaborn diverging palette
- Scatter matrix / pairplot — Seaborn
- Interactive scatter plots and distribution charts — Plotly
- Natural Language to Chart — describe a chart in Hinglish, AI generates it

### 🤖 AI Features (Groq Llama 3.3 — Free)
- AI chatbot — ask anything about your data in Hinglish
- Executive summary — headline finding + key insights with numbers
- Data story — narrative that tells the story of what the data reveals
- Action recommendations — immediate actions with impact/effort/timeline
- Natural language to chart — "sales ka bar chart banao category wise"

### 🔮 Machine Learning
- Regression — Linear, Ridge, Random Forest, Gradient Boosting (auto-compares all 4)
- Classification — Logistic Regression, Random Forest (auto-detects target type)
- Clustering — K-Means with auto-elbow detection, silhouette scoring, cluster profiles
- Forecasting — Linear trend + moving average, next N periods prediction

### ⚙️ Data Operations
- 8 transform operations: drop columns, fill missing, normalize, create computed columns, filter rows, sort, rename, drop duplicates
- Supports CSV, TSV, Excel (.xlsx), JSON upload
- Database connection — MySQL, PostgreSQL, SQLite (via SQLAlchemy)

### 📤 Export Options
- PDF Report — multi-page professional report with all stats and charts (ReportLab)
- PowerPoint — full dark-theme presentation with charts and insights (python-pptx)
- CSV + Excel export — with formatted headers (xlsxwriter)
- Email report — PDF sent via SMTP

### 👥 Multi-user Support
- Login/Register system
- Per-user session isolation
- No database required — stored in local JSON

---

## 🛠️ Tech Stack

| Layer | Technologies |
|-------|-------------|
| Backend | Flask, Flask-CORS, Gunicorn |
| Data Analysis | pandas, numpy, scipy |
| Machine Learning | scikit-learn |
| Visualizations | matplotlib, seaborn, plotly |
| AI/LLM | Groq API (Llama 3.3 70B) — free tier |
| Reports | ReportLab (PDF), python-pptx (PowerPoint) |
| Database | SQLAlchemy, PyMySQL, psycopg2 |
| Frontend | Vanilla JS, CSS (no frameworks) |

---

## 🚀 Getting Started

```bash
# Clone the repo
git clone https://github.com/Vaibhavsharma45/Auto_analyst
cd Auto_analyst

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Add your Groq API key (free at console.groq.com)
# Create .env file:
echo "GROQ_API_KEY=gsk_your_key_here" > .env

# Run
python app.py
```

Open `http://localhost:5000` — login screen will appear automatically.

---

## 📁 Project Structure

```
datamind-pro/
├── app.py                          ← Flask entry point
├── requirements.txt
├── runtime.txt                     ← Python 3.11 for Render
│
├── backend/
│   ├── analysis/
│   │   ├── eda_engine.py           ← Full EDA — pandas + scipy
│   │   ├── chart_generator.py      ← matplotlib + seaborn + plotly
│   │   ├── ml_engine.py            ← sklearn ML models
│   │   ├── insights_engine.py      ← AI summaries + recommendations
│   │   ├── problem_engine.py       ← Goal definition + validation
│   │   ├── ppt_generator.py        ← PowerPoint generation
│   │   └── report_generator.py     ← PDF report
│   ├── routes/                     ← 9 Flask Blueprints
│   └── utils/                      ← DB, email, auth, session, loader
│
└── frontend/
    ├── templates/index.html
    └── static/
        ├── css/main.css
        └── js/app.js
```

---

## 🌐 Deployment

Deployed on Render. Add these environment variables in Render dashboard:

```
GROQ_API_KEY = your_groq_key
SECRET_KEY   = any_random_string
FLASK_ENV    = production
```

---

## 📝 What I Learned Building This

- Integrating multiple Python data science libraries (pandas, scipy, sklearn, seaborn, plotly) into a single web app
- Building a proper Flask REST API with multiple blueprints
- Generating professional PDFs and PowerPoints programmatically
- Working with the Groq API for free LLM inference
- Handling large file uploads, in-memory session management
- Building a complete dark-theme UI in vanilla JS without any frontend framework

---

*Made with ❤️ by Vaibhav Sharma*
