<div align="center">

# ⚡ DataMind Pro

### AI-Powered Data Analysis Platform

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-datamind--pro.onrender.com-58a6ff?style=for-the-badge)](https://datamind-pro.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70B-F55036?style=for-the-badge)](https://groq.com)
[![Render](https://img.shields.io/badge/Deployed_on-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://render.com)

<br/>

> Upload any dataset → Get professional EDA, ML predictions, AI insights & action plan in minutes.
> Works like a **senior data analyst** — without writing a single line of code.

<br/>

```
📂 Upload CSV/Excel  →  📊 Auto EDA  →  🤖 ML Models  →  💬 Ask AI  →  📤 Export Report
```

</div>

---

## 🎯 The Problem I Solved

Every data analysis project starts the same way — clean the data, write matplotlib code, identify patterns, summarize findings. **Hours of repetitive work** before you get to the interesting part.

DataMind Pro automates the **entire workflow** so you can focus on decisions, not code.

---

## 🚀 Live Demo

<div align="center">

**[→ Try it now: datamind-pro.onrender.com](https://datamind-pro.onrender.com)**

> ⚠️ Free tier — app may take 30–60 seconds to wake up on first visit.

</div>

---

## ✨ Features

### 📊 6-Step Analysis Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│  1️⃣ Ask        2️⃣ Collect    3️⃣ Clean     4️⃣ Analyze           │
│  Goal Wizard → Upload Data → Transform → EDA + Charts          │
│                                                                  │
│  5️⃣ Insights   6️⃣ Actions                                       │
│  AI Summary  → Action Plan                                      │
└─────────────────────────────────────────────────────────────────┘
```

| Step | Feature | Details |
|------|---------|---------|
| 1️⃣ | **Goal Wizard** | 6 templates — Sales, HR, Finance, Operations, Customer, Custom |
| 2️⃣ | **Data Upload** | CSV, Excel, JSON, TSV — up to 100MB |
| 3️⃣ | **Clean & Transform** | 10 operations — fill missing, normalize, filter, rename, sort |
| 4️⃣ | **Analyze Patterns** | Full EDA — stats, correlations, distributions, outliers |
| 5️⃣ | **Communicate Insights** | AI executive summary + data story narrative |
| 6️⃣ | **Recommend Actions** | Prioritized plan with impact / effort / timeline |

---

### 📈 Charts & Visualizations

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Distribution │  │  Heatmap     │  │  Box Plots   │  │   Scatter    │
│  Dashboard   │  │ Correlation  │  │  Violin Plots│  │   Matrix     │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
┌──────────────┐  ┌──────────────────────────────────────────────────┐
│   Q-Q Plots  │  │  🗣️ NL to Chart — "sales ka bar chart banao" → ✅ │
└──────────────┘  └──────────────────────────────────────────────────┘
```

---

### 🤖 Machine Learning Models

```
📈 Regression          🏷️ Classification      🔵 Clustering
─────────────          ──────────────────      ─────────────
Linear Regression      Logistic Regression     K-Means (auto k)
Ridge Regression       Random Forest           Cluster Profiles
Random Forest    ───▶  Best model auto-picked  Silhouette Score
Gradient Boosting      Feature importance      
R�, RMSE, MAE          Accuracy %              

🔮 Forecasting
──────────────
Linear Trend + Moving Average → Future predictions with chart
```

---

### 💬 AI Features

```
┌─────────────────────────────────────────────────────────────┐
│  Powered by Groq Llama 3.3 70B (Free API)                   │
│                                                              │
│  💬 Chatbot     → Ask anything about your data (Hinglish ✅) │
│  📋 Summary     → Executive insights with real numbers       │
│  📖 Data Story  → Narrative arc of your dataset             │
│  🎯 Actions     → What to do next — with evidence           │
└─────────────────────────────────────────────────────────────┘
```

---

### 📤 Export Options

| Format | Tool | Content |
|--------|------|---------|
| 📄 PDF Report | ReportLab | Full analysis with charts |
| 📽️ PowerPoint | python-pptx | 9-slide dark theme deck |
| 📊 Excel | xlsxwriter | Cleaned dataset |
| ⬇️ CSV | pandas | Raw export |

---

## 🛠️ Tech Stack

```
Backend          Data & ML           Visualizations      AI
────────         ─────────           ──────────────      ──
Flask            pandas              matplotlib          Groq API
Flask-CORS        numpy               seaborn             Llama 3.3 70B
Gunicorn         scipy               plotly
                 statsmodels         
                 scikit-learn        Reports
                                     ───────
Database         Auth                ReportLab (PDF)
────────         ────                python-pptx
SQLAlchemy       JSON-based          xlsxwriter
PyMySQL          Session store
psycopg2
```

---

## 🚀 Run Locally

```bash
# Clone
git clone https://github.com/Vaibhavsharma45/Auto_analyst
cd Auto_analyst

# Setup virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Add your free Groq API key
echo "GROQ_API_KEY=gsk_your_key_here" > .env
echo "SECRET_KEY=any-random-string" >> .env

# Run
python app.py
# → Open http://localhost:5000
```

**Get free Groq API key (no credit card):** [console.groq.com](https://console.groq.com)

---

## 📁 Project Structure

```
datamind-pro/
├── app.py                          ← Flask entry point
├── requirements.txt
├── backend/
│   ├── analysis/
│   │   ├── eda_engine.py           ← Full EDA (pandas + scipy)
│   │   ├── chart_generator.py      ← matplotlib + seaborn + plotly
│   │   ├── ml_engine.py            ← sklearn ML models
│   │   ├── insights_engine.py      ← Groq AI summaries
│   │   ├── ppt_generator.py        ← PowerPoint generation
│   │   └── report_generator.py     ← PDF report
│   ├── routes/                     ← 9 Flask Blueprints
│   │   ├── upload_routes.py
│   │   ├── analysis_routes.py
│   │   ├── chart_routes.py
│   │   ├── ml_routes.py
│   │   ├── extras_routes.py        ← DB, Email, PPT, NL-chart
│   │   ├── chat_routes.py          ← Groq chatbot
│   │   ├── workflow_routes.py
│   │   ├── report_routes.py
│   │   └── auth_routes.py
│   └── utils/
│       ├── data_loader.py
│       ├── session_store.py
│       ├── db_connector.py         ← MySQL / PostgreSQL / SQLite
│       ├── email_sender.py         ← SMTP PDF email
│       └── auth.py                 ← Multi-user auth
└── frontend/
    ├── templates/index.html        ← Single page app
    └── static/
        ├── css/main.css            ← Dark theme (Syne font)
        └── js/app.js               ← All frontend logic (~1100 lines)
```

---

## 💡 What I Learned

- Building a production **Flask REST API** with 9 Blueprints
- Integrating **pandas + scipy + sklearn + plotly** in one app
- Generating professional **PDFs and PowerPoints** programmatically
- Working with **Groq API** for free LLM inference (Llama 3.3 70B)
- Building a complete **dark-theme SPA** in vanilla JS (no React)
- Handling large file uploads and **in-memory session management**
- Deploying Flask on **Render** with proper CORS setup
- Building a full **multi-user auth system** from scratch

---

<div align="center">

Made with ❤️ by **Vaibhav Sharma**

[![GitHub](https://img.shields.io/badge/GitHub-Vaibhavsharma45-181717?style=flat-square&logo=github)](https://github.com/Vaibhavsharma45)

⭐ Star this repo if you found it useful!

</div>