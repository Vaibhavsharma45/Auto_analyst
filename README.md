# ⚡ DataMind Pro — AI-Powered Data Analysis Platform

> Like hiring a senior data analyst — upload any dataset and get full EDA, statistical analysis, charts, quality reports, and an AI chatbot. All powered by **pandas, numpy, seaborn, matplotlib, scipy, scikit-learn, and Claude AI**.

---

## 🚀 Quick Start

```bash
# 1. Clone / extract the project
cd datamind-pro

# 2. Run setup (installs all dependencies)
chmod +x setup.sh run.sh
./setup.sh

# 3. Add your Anthropic API key
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env

# 4. Start the server
./run.sh

# 5. Open browser
open http://localhost:5000
```

---

## 📦 Tech Stack

| Layer | Libraries |
|-------|-----------|
| **Backend** | Flask, Flask-CORS |
| **Data Analysis** | pandas, numpy |
| **Statistics** | scipy, statsmodels |
| **Visualizations** | matplotlib, seaborn, plotly |
| **ML** | scikit-learn (PCA, preprocessing) |
| **Reports** | reportlab, fpdf2 |
| **Excel** | openpyxl, xlsxwriter |
| **AI** | Anthropic Claude (claude-sonnet-4-20250514) |

---

## 🧠 Features

### 📊 Automatic EDA (Exploratory Data Analysis)
- **Distribution plots** — KDE + histogram for every numeric column
- **Box plots** — outlier visualization using IQR method
- **Correlation heatmap** — Seaborn diverging palette
- **Scatter matrix (pairplot)** — Seaborn pairplot with category coloring
- **Q-Q plots** — normality assessment for all numeric columns
- **Violin plots** — distribution by category
- **Missing values chart** — visual missing data profile
- **Interactive Plotly charts** — scatter with trendlines, distribution histograms

### 📈 Statistical Analysis
- **Descriptive stats**: mean, median, mode, std, variance, range, IQR
- **Percentiles**: P1, P5, P10, P25, P50, P75, P90, P95, P99
- **Normality tests**: Shapiro-Wilk (n≤5000) / D'Agostino-Pearson
- **Skewness & Kurtosis** analysis
- **Outlier detection**: IQR fence method
- **ANOVA group analysis**: categorical vs numeric significance
- **PCA Summary**: explained variance, loadings

### 🔍 Data Quality Report
- Missing value analysis (count + percentage per column)
- Duplicate row detection
- Outlier count per column
- High cardinality detection
- Skewness flags
- **Quality Score** (0-100)
- Actionable recommendations

### 🔗 Correlation Analysis
- **Pearson, Spearman, Kendall** matrices
- Strong pair detection (|r| ≥ 0.5)
- Color-coded heatmap values

### ⚙️ Data Transformation
- Drop duplicates
- Drop columns
- Fill missing values (mean/median/mode/zero/ffill/bfill)
- Normalize columns (Min-Max, Z-Score, Log)
- Create new computed columns
- Filter rows (pandas query syntax)
- Sort by any column

### 🤖 AI Chatbot (Claude-powered)
- Answer any question about your data
- Get statistical insights in Hinglish
- Request transformations via natural language
- Auto-applies transforms and re-runs analysis

### 📄 PDF Report
- Professional multi-page PDF report
- Dataset overview, all stats, correlations
- Quality issues + recommendations
- All charts embedded
- Generated with ReportLab

### ⬇ Data Export
- Download transformed data as **CSV**
- Download as **Excel** (with formatted headers)
- Download full **PDF analysis report**

---

## 📁 Project Structure

```
datamind-pro/
├── app.py                          ← Flask entry point
├── requirements.txt                ← All Python dependencies
├── .env.example                    ← Environment template
├── setup.sh                        ← One-time setup
├── run.sh                          ← Start server
│
├── backend/
│   ├── analysis/
│   │   ├── eda_engine.py           ← Core EDA: all statistics
│   │   ├── chart_generator.py      ← matplotlib + seaborn + plotly charts
│   │   └── report_generator.py     ← PDF report (reportlab)
│   ├── utils/
│   │   ├── data_loader.py          ← CSV/Excel/JSON loading
│   │   └── session_store.py        ← In-memory session + transforms
│   └── routes/
│       ├── upload_routes.py        ← /api/upload/*
│       ├── analysis_routes.py      ← /api/analysis/*
│       ├── chart_routes.py         ← /api/charts/*
│       ├── report_routes.py        ← /api/report/pdf
│       └── chat_routes.py          ← /api/chat/message
│
├── frontend/
│   ├── templates/
│   │   └── index.html              ← Main HTML template
│   └── static/
│       ├── css/main.css            ← Dark professional theme
│       └── js/app.js               ← Full frontend logic
│
├── data/
│   ├── uploads/                    ← Uploaded files stored here
│   └── samples/                    ← Sample datasets
│
└── reports/output/                 ← Generated PDF reports
```

---

## 🔌 API Reference

| Endpoint | Method | Description |
|---------|--------|-------------|
| `POST /api/upload/file` | POST | Upload CSV/Excel file |
| `POST /api/upload/text` | POST | Parse CSV from text |
| `GET /api/analysis/full/{sid}` | GET | Run full EDA |
| `GET /api/analysis/overview/{sid}` | GET | Dataset overview only |
| `GET /api/analysis/preview/{sid}` | GET | First N rows |
| `POST /api/analysis/transform/{sid}` | POST | Apply transformation |
| `GET /api/analysis/download/csv/{sid}` | GET | Download as CSV |
| `GET /api/analysis/download/excel/{sid}` | GET | Download as Excel |
| `GET /api/charts/all/{sid}` | GET | Generate all charts |
| `GET /api/charts/image/{sid}/{name}` | GET | Get chart as PNG |
| `GET /api/report/pdf/{sid}` | GET | Download PDF report |
| `POST /api/chat/message/{sid}` | POST | Chat with AI |

---

## 🌐 Supported File Formats
- **CSV** (.csv) — comma, semicolon, pipe, or tab separated
- **TSV** (.tsv) — tab separated
- **Excel** (.xlsx, .xls)
- **JSON** (.json) — array of objects
- **Text** (.txt) — any delimited format

---

## 💬 Chat Examples (Hinglish)

- *"Dataset ka full summary do"*
- *"Salary column mein kitne outliers hain?"*
- *"Age aur salary ke beech correlation kitna hai?"*
- *"Missing values fill kar do median se"*
- *"Profit margin column create karo: profit / sales * 100"*
- *"30 se kam age wale employees dikhao"*
- *"Kaunsa department sabse zyada salary deta hai?"*

---

