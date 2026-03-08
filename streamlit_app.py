"""
DataMind Pro — Streamlit Version
AI-Powered Data Analysis Platform
Deploy on Streamlit Cloud — free!
"""
import streamlit as st
import pandas as pd
import numpy as np
import sys, os, io, json, warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass

# ── PAGE CONFIG ──────────────────────────────────────
st.set_page_config(
    page_title="DataMind Pro ⚡",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── THEME CSS ────────────────────────────────────────
st.markdown("""
<style>
/* Dark theme */
.stApp { background: #0d1117 !important; }
[data-testid="stSidebar"] { background: #010409 !important; border-right: 1px solid #21262d; }
.stApp header { background: #0d1117 !important; }
h1,h2,h3,h4 { color: #e6edf3 !important; }
p, li, label { color: #c9d1d9 !important; }
[data-testid="stMetricValue"] { color: #58a6ff !important; font-weight: 800 !important; }
[data-testid="stMetricLabel"] { color: #8b949e !important; }
[data-testid="metric-container"] { background: #161b22; border: 1px solid #21262d; border-radius: 10px; padding: 12px; }
.stButton > button { background: linear-gradient(135deg,#388bfd,#58a6ff) !important; color: #fff !important; border: none !important; border-radius: 8px !important; font-weight: 700 !important; }
.stButton > button:hover { background: linear-gradient(135deg,#58a6ff,#79c0ff) !important; }
div[data-testid="stDataFrame"] { background: #161b22; border-radius: 10px; }
.stSelectbox > div > div, .stTextInput > div > div { background: #161b22 !important; border-color: #21262d !important; color: #e6edf3 !important; }
.stTabs [data-baseweb="tab-list"] { background: #0d1117; border-bottom: 1px solid #21262d; }
.stTabs [data-baseweb="tab"] { color: #8b949e !important; background: transparent !important; }
.stTabs [aria-selected="true"] { color: #58a6ff !important; border-bottom: 2px solid #58a6ff !important; }
.stExpander { background: #161b22; border: 1px solid #21262d; border-radius: 10px; }
div[data-testid="stChatMessage"] { background: #161b22; border-radius: 10px; border: 1px solid #21262d; }
.stSlider > div > div > div { background: #58a6ff !important; }
.insight-box { background: #161b22; border-left: 4px solid #58a6ff; padding: 14px 18px; border-radius: 0 10px 10px 0; margin: 8px 0; }
.action-box { background: #161b22; border-left: 4px solid #3fb950; padding: 14px 18px; border-radius: 0 10px 10px 0; margin: 8px 0; }
.warn-box { background: #161b22; border-left: 4px solid #d29922; padding: 14px 18px; border-radius: 0 10px 10px 0; margin: 8px 0; }
.stProgress > div > div > div { background: linear-gradient(90deg,#58a6ff,#bc8cff) !important; }
</style>
""", unsafe_allow_html=True)

PALETTE = ["#58a6ff","#bc8cff","#3fb950","#d29922","#f85149","#79c0ff","#ffa657","#ff7b72"]

# ── SESSION STATE ────────────────────────────────────
for k, v in {
    "df": None, "filename": None, "analysis": None,
    "goal_type": "Custom Analysis", "goal_question": "",
    "chat_history": [], "ml_cache": {}
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── GROQ AI ──────────────────────────────────────────
def ask_ai(prompt: str, system: str = "You are an expert data analyst. Be specific with numbers. Use Hinglish naturally.", history: list = None) -> str:
    import requests
    key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
    if not key:
        return "⚠️ GROQ_API_KEY not configured. Add it in Streamlit Cloud → App Settings → Secrets."
    msgs = [{"role": "system", "content": system}]
    if history:
        msgs += history[-8:]
    msgs.append({"role": "user", "content": prompt})
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": "llama-3.3-70b-versatile", "messages": msgs, "max_tokens": 2000, "temperature": 0.7},
            timeout=45
        )
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        return f"❌ API error {r.status_code}: {r.text[:200]}"
    except Exception as e:
        return f"❌ Request failed: {e}"


def ask_ai_json(prompt: str) -> dict:
    reply = ask_ai(prompt, system="You are a data analyst. Return ONLY valid JSON, no markdown, no extra text.")
    try:
        clean = reply.replace("```json","").replace("```","").strip()
        return json.loads(clean)
    except:
        return {"_raw": reply}


# ── DATA LOADER ──────────────────────────────────────
def load_file(file) -> pd.DataFrame:
    name = file.name.lower()
    if name.endswith(".csv"):    return pd.read_csv(file)
    if name.endswith(".tsv"):    return pd.read_csv(file, sep="\t")
    if name.endswith((".xlsx",".xls")): return pd.read_excel(file)
    if name.endswith(".json"):   return pd.read_json(file)
    raise ValueError(f"Unsupported format: {name.split('.')[-1]}")


# ── ANALYSIS ENGINE ──────────────────────────────────
@st.cache_data(show_spinner=False)
def run_eda(df_hash: str, _df: pd.DataFrame) -> dict:
    try:
        from backend.analysis.eda_engine import EDAEngine
        return EDAEngine(_df).run_full_analysis()
    except Exception as e:
        return _fallback_eda(_df)


def _fallback_eda(df: pd.DataFrame) -> dict:
    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    cat_cols = df.select_dtypes(include="object").columns.tolist()
    ns = {}
    for col in num_cols:
        s = df[col].dropna()
        if len(s) == 0: continue
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        outliers = int(((s < q1-1.5*iqr) | (s > q3+1.5*iqr)).sum())
        ns[col] = {"mean": round(float(s.mean()),2), "median": round(float(s.median()),2),
                   "std": round(float(s.std()),2), "min": round(float(s.min()),2),
                   "max": round(float(s.max()),2), "outliers": {"count": outliers},
                   "skewness": round(float(s.skew()),3)}
    cs = {}
    for col in cat_cols[:5]:
        vc = df[col].value_counts().head(5)
        cs[col] = {"unique_values": int(df[col].nunique()), "value_counts": vc.to_dict()}
    corr_pairs = []
    if len(num_cols) >= 2:
        corr_m = df[num_cols].corr()
        for i in range(len(num_cols)):
            for j in range(i+1, len(num_cols)):
                r = float(corr_m.iloc[i,j])
                if abs(r) >= 0.5:
                    corr_pairs.append({"col1": num_cols[i], "col2": num_cols[j],
                                       "pearson_r": round(r,3), "strength": "strong" if abs(r)>=0.7 else "moderate"})
    corr_pairs.sort(key=lambda x: abs(x["pearson_r"]), reverse=True)
    missing = int(df.isnull().sum().sum())
    dups = int(df.duplicated().sum())
    score = 100
    issues = []
    if missing > 0:
        pct = missing/(df.shape[0]*df.shape[1])*100
        score -= min(30, int(pct*3))
        issues.append({"severity":"warning","message":f"{missing} missing cells ({pct:.1f}%)"})
    if dups > 0:
        score -= min(20, dups)
        issues.append({"severity":"warning","message":f"{dups} duplicate rows found"})
    for col, s in ns.items():
        if s["outliers"]["count"] > len(df)*0.05:
            issues.append({"severity":"info","message":f"{col}: {s['outliers']['count']} outliers detected"})
    return {
        "overview": {"shape": {"rows": len(df), "columns": len(df.columns)},
                     "missing": {"total_missing_cells": missing},
                     "duplicates": {"duplicate_rows": dups},
                     "column_types": {"numeric": num_cols, "categorical": cat_cols}},
        "numeric_stats": ns, "categorical_stats": cs,
        "correlations": {"strong_pairs": corr_pairs[:8]},
        "quality_report": {"quality_score": max(0,score), "issues": issues,
                          "recommendations": ["Fix missing values","Remove duplicates"] if issues else [],
                          "total_issues": len(issues)}
    }


# ══════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚡ DataMind Pro `v3`")
    st.caption("AI-Powered Data Analysis")
    st.markdown("---")

    if st.session_state.df is not None:
        df = st.session_state.df
        a  = st.session_state.analysis or {}
        ov = a.get("overview", {})
        sh = ov.get("shape", {})
        qr = a.get("quality_report", {})
        score = qr.get("quality_score", 0)
        icon = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"

        st.markdown(f"**📁 {st.session_state.filename}**")
        st.markdown(f"`{sh.get('rows',0):,} rows × {sh.get('columns',0)} cols`")
        st.markdown(f"{icon} Quality Score: **{score}/100**")
        if st.session_state.goal_question:
            st.markdown(f"🎯 *\"{st.session_state.goal_question[:50]}...\"*" if len(st.session_state.goal_question)>50 else f"🎯 *\"{st.session_state.goal_question}\"*")
        st.markdown("---")

        page = st.radio("", [
            "📊 Overview", "🧹 Clean & Transform", "📈 Charts & Viz",
            "🤖 ML Predictions", "💬 AI Chat", "📢 Insights",
            "🎯 Recommendations", "📋 Data Preview"
        ], label_visibility="collapsed")

        st.markdown("---")
        st.markdown("**📥 Export**")
        c1, c2 = st.columns(2)
        csv_data = df.to_csv(index=False).encode()
        c1.download_button("⬇ CSV", csv_data, f"{st.session_state.filename}.csv", "text/csv", use_container_width=True)
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="xlsxwriter") as w:
            df.to_excel(w, index=False)
        c2.download_button("📊 Excel", buf.getvalue(), f"{st.session_state.filename}.xlsx", use_container_width=True)

        st.markdown("")
        if st.button("↺ New Analysis", use_container_width=True):
            for k in ["df","filename","analysis","chat_history","ml_cache"]:
                st.session_state[k] = None if k not in ["chat_history","ml_cache"] else ([] if k=="chat_history" else {})
            st.rerun()
    else:
        page = "🏠 Home"


# ══════════════════════════════════════════════════════
# HOME / UPLOAD
# ══════════════════════════════════════════════════════
if st.session_state.df is None:
    st.markdown("<h1 style='text-align:center;font-size:52px'>⚡ Data<span style='color:#58a6ff'>Mind</span> Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#8b949e;font-size:18px;margin-bottom:40px'>AI-Powered Data Analysis Platform • Powered by Groq Llama 3.3</p>", unsafe_allow_html=True)

    # Feature pills
    cols = st.columns(6)
    for col, feat in zip(cols, ["📊 EDA", "🤖 ML", "💬 AI Chat", "📈 Charts", "📢 Insights", "🎯 Actions"]):
        col.markdown(f"<div style='text-align:center;background:#161b22;border:1px solid #21262d;border-radius:20px;padding:6px;font-size:13px;color:#58a6ff'>{feat}</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown("### 🎯 Step 1 — Define Your Goal")
        goal_type = st.selectbox("Analysis Type", [
            "🛒 Sales Performance", "👥 Customer Analysis",
            "🏢 HR / Workforce", "💰 Financial Analysis",
            "⚙️ Operations", "🔬 Custom Analysis"
        ])
        goal_q = st.text_input("Your Business Question", placeholder="e.g. Which products are underperforming this quarter?")
        st.session_state.goal_type = goal_type
        st.session_state.goal_question = goal_q

        st.markdown("### 📂 Step 2 — Upload Data")
        uploaded = st.file_uploader("CSV • Excel • JSON • TSV (max 100MB)", type=["csv","xlsx","xls","json","tsv"], label_visibility="collapsed")

    with col2:
        st.markdown("### 🚀 Or try a sample dataset")
        samples = {
            "🛒 Sales Data": ("sales_sample.csv", "month,product,category,sales,units,profit,region,target\nJan,Laptop,Electronics,145000,29,42000,North,130000\nJan,Phone,Electronics,89000,89,22000,South,80000\nJan,Shoes,Apparel,34000,113,9000,East,40000\nFeb,Laptop,Electronics,167000,33,48000,North,150000\nFeb,Phone,Electronics,95000,95,24000,West,90000\nFeb,Shoes,Apparel,41000,136,11000,South,38000\nMar,Laptop,Electronics,139000,27,40000,East,145000\nMar,TV,Electronics,78000,15,18000,North,75000\nApr,Phone,Electronics,103000,103,26000,North,95000\nApr,Laptop,Electronics,188000,37,55000,South,170000\nMay,Laptop,Electronics,172000,34,50000,West,160000\nJun,TV,Electronics,101000,19,23000,North,95000\nJun,Laptop,Electronics,195000,39,57000,West,180000"),
            "👥 HR Data": ("hr_sample.csv", "id,name,department,age,salary,experience,rating,city,gender,promoted\nE001,Rahul Sharma,Engineering,28,75000,4,4.2,Delhi,M,No\nE002,Priya Patel,Marketing,32,65000,7,4.5,Mumbai,F,Yes\nE003,Amit Kumar,Engineering,35,92000,10,4.8,Bangalore,M,Yes\nE004,Sneha Gupta,HR,27,48000,3,3.9,Delhi,F,No\nE005,Vikram Singh,Engineering,30,82000,6,4.3,Hyderabad,M,No\nE006,Anita Joshi,Marketing,29,60000,5,4.1,Pune,F,No\nE007,Rajesh Verma,Finance,40,110000,15,4.6,Mumbai,M,Yes\nE008,Kavita Mehta,Engineering,26,68000,2,3.8,Bangalore,F,No\nE009,Suresh Nair,HR,33,52000,8,4.0,Chennai,M,No\nE010,Deepa Reddy,Finance,37,98000,12,4.7,Hyderabad,F,Yes"),
            "📦 E-commerce": ("ecommerce_sample.csv", "order_id,product,category,price,qty,discount,rating,delivery_days,returned\nORD001,Wireless Earbuds,Electronics,2499,1,10,4.3,3,No\nORD002,Cotton Kurta,Clothing,899,2,5,4.1,5,No\nORD003,Python Book,Books,599,1,0,4.7,4,No\nORD004,Running Shoes,Footwear,3499,1,15,3.9,6,Yes\nORD005,Bluetooth Speaker,Electronics,1999,1,8,4.5,3,No\nORD006,Smart Watch,Electronics,8999,1,12,4.6,3,Yes\nORD007,Yoga Mat,Sports,1499,1,0,4.4,5,No\nORD008,Formal Shoes,Footwear,2999,1,5,4.2,7,No\nORD009,Jeans,Clothing,1299,1,10,4.0,5,No\nORD010,Cricket Bat,Sports,2999,1,5,4.6,7,No"),
        }

        for name, (fname, csv_data) in samples.items():
            if st.button(name, use_container_width=True, key=f"sample_{name}"):
                df = pd.read_csv(io.StringIO(csv_data))
                st.session_state.df = df
                st.session_state.filename = fname
                with st.spinner("🔄 Running analysis..."):
                    st.session_state.analysis = run_eda(str(df.shape), df)
                st.success("✅ Dataset loaded!")
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='background:#161b22;border:1px solid #21262d;border-radius:12px;padding:16px'>
        <p style='color:#8b949e;font-size:13px;margin:0'>
        ✅ pandas + scipy EDA<br>
        ✅ matplotlib + seaborn charts<br>
        ✅ sklearn ML models<br>
        ✅ Groq AI insights<br>
        ✅ CSV / Excel export<br>
        ✅ No data stored — 100% private
        </p>
        </div>
        """, unsafe_allow_html=True)

    if uploaded:
        try:
            df = load_file(uploaded)
            st.session_state.df = df
            st.session_state.filename = uploaded.name
            with st.spinner("🔄 Running full analysis..."):
                st.session_state.analysis = run_eda(str(df.shape)+uploaded.name, df)
            st.success(f"✅ {uploaded.name} loaded — {len(df):,} rows × {len(df.columns)} cols")
            st.rerun()
        except Exception as e:
            st.error(f"❌ {e}")

# ══════════════════════════════════════════════════════
# ANALYSIS PAGES
# ══════════════════════════════════════════════════════
else:
    df = st.session_state.df
    a  = st.session_state.analysis or _fallback_eda(df)
    ov = a.get("overview", {})
    sh = ov.get("shape", {})
    ns = a.get("numeric_stats", {})
    cs = a.get("categorical_stats", {})
    qr = a.get("quality_report", {})
    corr = a.get("correlations", {})
    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    cat_cols = df.select_dtypes(include="object").columns.tolist()

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    def dark_fig(w=10, h=5):
        fig, ax = plt.subplots(figsize=(w, h))
        fig.patch.set_facecolor("#0d1117")
        ax.set_facecolor("#161b22")
        ax.tick_params(colors="#8b949e")
        ax.xaxis.label.set_color("#c9d1d9")
        ax.yaxis.label.set_color("#c9d1d9")
        ax.title.set_color("#e6edf3")
        for spine in ax.spines.values():
            spine.set_edgecolor("#21262d")
        ax.grid(True, color="#21262d", linewidth=0.5)
        return fig, ax

    # ── OVERVIEW ──────────────────────────────────────
    if page == "📊 Overview":
        st.markdown(f"## 📊 Overview — `{st.session_state.filename}`")

        m1,m2,m3,m4,m5,m6 = st.columns(6)
        m1.metric("Rows", f"{sh.get('rows',0):,}")
        m2.metric("Columns", sh.get('columns',0))
        m3.metric("Missing", ov.get('missing',{}).get('total_missing_cells',0))
        m4.metric("Duplicates", ov.get('duplicates',{}).get('duplicate_rows',0))
        m5.metric("Numeric Cols", len(num_cols))
        m6.metric("Quality Score", f"{qr.get('quality_score',0)}/100")

        st.markdown("---")

        col1, col2 = st.columns([1.5,1])
        with col1:
            if ns:
                st.markdown("### 📈 Numeric Statistics")
                stats_rows = []
                for c, s in ns.items():
                    stats_rows.append({"Column":c, "Mean":s.get("mean"), "Median":s.get("median"),
                                       "Std":s.get("std"), "Min":s.get("min"), "Max":s.get("max"),
                                       "Outliers":s.get("outliers",{}).get("count",0)})
                st.dataframe(pd.DataFrame(stats_rows), use_container_width=True, hide_index=True)

        with col2:
            strong = corr.get("strong_pairs", [])
            if strong:
                st.markdown("### 🔗 Top Correlations")
                for p in strong[:6]:
                    r = p.get("pearson_r", 0)
                    bar_pct = int(abs(r) * 100)
                    color = "#3fb950" if r > 0 else "#f85149"
                    st.markdown(f"""
                    <div style='margin:6px 0;background:#161b22;border-radius:8px;padding:10px'>
                    <div style='display:flex;justify-content:space-between;margin-bottom:5px'>
                    <span style='color:#c9d1d9;font-size:13px'>{p['col1']} ↔ {p['col2']}</span>
                    <span style='color:{color};font-weight:700'>{r}</span></div>
                    <div style='background:#21262d;border-radius:4px;height:6px'>
                    <div style='background:{color};width:{bar_pct}%;height:6px;border-radius:4px'></div></div>
                    </div>""", unsafe_allow_html=True)

            issues = qr.get("issues", [])
            if issues:
                st.markdown("### ⚠️ Quality Issues")
                for issue in issues[:5]:
                    sev = issue.get("severity","info")
                    if sev == "critical": st.error(issue["message"])
                    elif sev == "warning": st.warning(issue["message"])
                    else: st.info(issue["message"])

        # Categorical preview
        if cs:
            st.markdown("### 🏷 Categorical Columns")
            cat_display_cols = st.columns(min(len(cs), 3))
            for i, (col_name, s) in enumerate(list(cs.items())[:3]):
                with cat_display_cols[i]:
                    st.markdown(f"**{col_name}** ({s.get('unique_values',0)} unique)")
                    vc = s.get("value_counts", {})
                    if vc:
                        fig, ax = dark_fig(4, 3)
                        items = list(vc.items())[:6]
                        labels = [str(x[0])[:15] for x in items]
                        vals = [x[1] for x in items]
                        ax.bar(labels, vals, color=PALETTE[:len(labels)])
                        plt.xticks(rotation=30, ha="right", fontsize=8)
                        fig.tight_layout()
                        st.pyplot(fig)
                        plt.close(fig)

    # ── CLEAN ─────────────────────────────────────────
    elif page == "🧹 Clean & Transform":
        st.markdown("## 🧹 Clean & Transform")
        st.markdown(f"`{sh.get('rows',0):,} rows × {sh.get('columns',0)} cols` → apply operations below")

        c1, c2 = st.columns([1, 1.5])
        with c1:
            st.markdown("### ⚙️ Operations")
            op = st.selectbox("Operation", [
                "drop_duplicates", "drop_column", "fill_missing_mean",
                "fill_missing_median", "fill_missing_zero", "normalize",
                "rename_column", "filter_rows", "sort_ascending",
                "sort_descending", "drop_missing_rows"
            ])
            col_sel = st.selectbox("Column (if needed)", ["—"] + df.columns.tolist())
            extra = ""
            if op == "rename_column":
                extra = st.text_input("New column name")
            elif op == "filter_rows":
                extra = st.text_input("Filter value (contains)")

            if st.button("▶ Apply Operation", use_container_width=True):
                try:
                    new_df = df.copy()
                    msg = ""
                    if op == "drop_duplicates":
                        before = len(new_df)
                        new_df = new_df.drop_duplicates()
                        msg = f"Removed {before - len(new_df)} duplicates"
                    elif op == "drop_column" and col_sel != "—":
                        new_df = new_df.drop(columns=[col_sel])
                        msg = f"Dropped column: {col_sel}"
                    elif op == "fill_missing_mean" and col_sel != "—":
                        new_df[col_sel] = new_df[col_sel].fillna(new_df[col_sel].mean())
                        msg = f"Filled {col_sel} with mean"
                    elif op == "fill_missing_median" and col_sel != "—":
                        new_df[col_sel] = new_df[col_sel].fillna(new_df[col_sel].median())
                        msg = f"Filled {col_sel} with median"
                    elif op == "fill_missing_zero" and col_sel != "—":
                        new_df[col_sel] = new_df[col_sel].fillna(0)
                        msg = f"Filled {col_sel} with 0"
                    elif op == "normalize" and col_sel != "—":
                        mn, mx = new_df[col_sel].min(), new_df[col_sel].max()
                        new_df[col_sel] = (new_df[col_sel] - mn) / (mx - mn + 1e-9)
                        msg = f"Normalized {col_sel} to [0,1]"
                    elif op == "rename_column" and col_sel != "—" and extra:
                        new_df = new_df.rename(columns={col_sel: extra})
                        msg = f"Renamed {col_sel} → {extra}"
                    elif op == "filter_rows" and col_sel != "—" and extra:
                        before = len(new_df)
                        new_df = new_df[new_df[col_sel].astype(str).str.contains(extra, na=False)]
                        msg = f"Filtered: {len(new_df)}/{before} rows kept"
                    elif op == "sort_ascending" and col_sel != "—":
                        new_df = new_df.sort_values(col_sel, ascending=True)
                        msg = f"Sorted by {col_sel} ascending"
                    elif op == "sort_descending" and col_sel != "—":
                        new_df = new_df.sort_values(col_sel, ascending=False)
                        msg = f"Sorted by {col_sel} descending"
                    elif op == "drop_missing_rows":
                        before = len(new_df)
                        new_df = new_df.dropna()
                        msg = f"Dropped {before - len(new_df)} rows with missing values"

                    if msg:
                        st.session_state.df = new_df
                        with st.spinner("Re-running analysis..."):
                            st.session_state.analysis = run_eda(str(new_df.shape)+op, new_df)
                        st.success(f"✅ {msg}")
                        st.rerun()
                    else:
                        st.warning("Select a valid column first")
                except Exception as e:
                    st.error(f"❌ {e}")

        with c2:
            st.markdown("### 📋 Current Data Preview")
            st.dataframe(df.head(20), use_container_width=True, hide_index=True)
            miss = df.isnull().sum()
            miss = miss[miss > 0]
            if not miss.empty:
                st.markdown("**Missing Values:**")
                st.dataframe(miss.reset_index().rename(columns={"index":"Column", 0:"Missing"}), use_container_width=True, hide_index=True)

    # ── CHARTS ────────────────────────────────────────
    elif page == "📈 Charts & Viz":
        st.markdown("## 📈 Charts & Visualizations")

        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Distributions", "🔗 Heatmap", "📦 Box Plots", "🔵 Scatter", "🛠 Custom"])

        with tab1:
            if num_cols:
                sel = st.multiselect("Columns", num_cols, default=num_cols[:min(3,len(num_cols))])
                if sel:
                    fig, axes = plt.subplots(1, len(sel), figsize=(5*len(sel), 4))
                    fig.patch.set_facecolor("#0d1117")
                    if len(sel) == 1: axes = [axes]
                    for i, col in enumerate(sel):
                        axes[i].set_facecolor("#161b22")
                        data = df[col].dropna()
                        axes[i].hist(data, bins=25, color=PALETTE[i%len(PALETTE)], alpha=0.85, edgecolor="none")
                        axes[i].set_title(col, color="#e6edf3")
                        axes[i].tick_params(colors="#8b949e")
                        for sp in axes[i].spines.values(): sp.set_edgecolor("#21262d")
                    fig.tight_layout()
                    st.pyplot(fig); plt.close(fig)
            else:
                st.info("No numeric columns found")

        with tab2:
            if len(num_cols) >= 2:
                sel2 = st.multiselect("Select columns", num_cols, default=num_cols[:min(8,len(num_cols))], key="hm")
                if len(sel2) >= 2:
                    corr_df = df[sel2].corr()
                    fig, ax = plt.subplots(figsize=(max(6,len(sel2)*1.1), max(5,len(sel2)*0.9)))
                    fig.patch.set_facecolor("#0d1117")
                    ax.set_facecolor("#161b22")
                    sns.heatmap(corr_df, annot=True, fmt=".2f", cmap="coolwarm",
                               center=0, ax=ax, linewidths=0.5, linecolor="#21262d",
                               cbar_kws={"shrink":0.8})
                    ax.tick_params(colors="#c9d1d9", labelsize=9)
                    ax.set_title("Correlation Heatmap", color="#e6edf3", fontsize=13)
                    fig.tight_layout(); st.pyplot(fig); plt.close(fig)
            else:
                st.info("Need 2+ numeric columns")

        with tab3:
            if num_cols:
                sel3 = st.multiselect("Columns", num_cols, default=num_cols[:min(4,len(num_cols))], key="bp")
                if sel3:
                    fig, axes = plt.subplots(1, len(sel3), figsize=(4*len(sel3), 5))
                    fig.patch.set_facecolor("#0d1117")
                    if len(sel3) == 1: axes = [axes]
                    for i, col in enumerate(sel3):
                        axes[i].set_facecolor("#161b22")
                        bp = axes[i].boxplot([df[col].dropna()], patch_artist=True,
                                            medianprops={"color":"#3fb950","linewidth":2.5},
                                            whiskerprops={"color":"#8b949e"},
                                            capprops={"color":"#8b949e"},
                                            flierprops={"marker":"o","markersize":3,"alpha":0.4,"markerfacecolor":PALETTE[i%len(PALETTE)]})
                        bp["boxes"][0].set(facecolor="#58a6ff22", edgecolor="#58a6ff")
                        axes[i].set_title(col, color="#e6edf3")
                        axes[i].set_xticks([])
                        axes[i].tick_params(colors="#8b949e")
                        for sp in axes[i].spines.values(): sp.set_edgecolor("#21262d")
                    fig.tight_layout(); st.pyplot(fig); plt.close(fig)

        with tab4:
            if len(num_cols) >= 2:
                c1, c2, c3 = st.columns(3)
                x = c1.selectbox("X axis", num_cols, key="sc_x")
                y = c2.selectbox("Y axis", num_cols, index=min(1,len(num_cols)-1), key="sc_y")
                hue = c3.selectbox("Color by (optional)", ["None"] + cat_cols, key="sc_hue")
                fig, ax = dark_fig(9, 5)
                if hue != "None" and hue in df.columns:
                    cats = df[hue].unique()
                    for i, cat in enumerate(cats[:8]):
                        mask = df[hue] == cat
                        ax.scatter(df[mask][x], df[mask][y], label=str(cat),
                                  color=PALETTE[i%len(PALETTE)], alpha=0.6, s=40)
                    ax.legend(framealpha=0.3, labelcolor="#c9d1d9")
                else:
                    ax.scatter(df[x], df[y], color="#58a6ff", alpha=0.5, s=30)
                ax.set_xlabel(x); ax.set_ylabel(y)
                ax.set_title(f"{x} vs {y}", color="#e6edf3")
                fig.tight_layout(); st.pyplot(fig); plt.close(fig)

        with tab5:
            st.markdown("**🛠 Build Your Own Chart**")
            c1, c2, c3 = st.columns(3)
            ctype = c1.selectbox("Chart type", ["bar","line","pie","area","histogram"])
            xcol = c2.selectbox("X / Category", df.columns.tolist(), key="cx")
            ycol = c3.selectbox("Y / Value", ["count"] + num_cols, key="cy")

            if st.button("⚡ Generate", use_container_width=True):
                try:
                    fig, ax = dark_fig(10, 5)
                    if ctype == "bar":
                        if ycol == "count":
                            data = df[xcol].value_counts().head(12)
                        else:
                            data = df.groupby(xcol)[ycol].sum().sort_values(ascending=False).head(12)
                        bars = ax.bar(data.index.astype(str), data.values,
                                     color=[PALETTE[i%len(PALETTE)] for i in range(len(data))])
                        plt.xticks(rotation=30, ha="right")
                        ax.set_ylabel(ycol)
                    elif ctype == "line":
                        ydata = df[ycol] if ycol != "count" else df[xcol].value_counts().sort_index()
                        ax.plot(range(len(ydata)), ydata.values, color="#58a6ff", linewidth=2.5)
                        ax.fill_between(range(len(ydata)), ydata.values, alpha=0.1, color="#58a6ff")
                        ax.set_ylabel(ycol)
                    elif ctype == "pie":
                        vc = df[xcol].value_counts().head(7)
                        wedges, texts, autotexts = ax.pie(vc.values, labels=vc.index,
                                                          colors=PALETTE[:len(vc)], autopct="%1.1f%%",
                                                          pctdistance=0.75,
                                                          wedgeprops={"edgecolor":"#0d1117","linewidth":2})
                        for t in texts: t.set_color("#c9d1d9")
                        for t in autotexts: t.set_color("#0d1117")
                    elif ctype == "area":
                        ydata = df[ycol] if ycol != "count" else df[xcol].value_counts().sort_index()
                        ax.fill_between(range(len(ydata)), ydata.values, alpha=0.4, color="#58a6ff")
                        ax.plot(range(len(ydata)), ydata.values, color="#58a6ff", linewidth=2)
                    elif ctype == "histogram":
                        col_h = ycol if ycol != "count" else xcol
                        ax.hist(df[col_h].dropna(), bins=30, color="#58a6ff", alpha=0.85, edgecolor="none")
                        ax.set_xlabel(col_h)
                    ax.set_title(f"{ctype.title()} — {xcol}", color="#e6edf3", fontsize=13)
                    fig.tight_layout(); st.pyplot(fig); plt.close(fig)
                except Exception as e:
                    st.error(f"Chart error: {e}")

    # ── ML MODELS ─────────────────────────────────────
    elif page == "🤖 ML Predictions":
        st.markdown("## 🤖 ML Predictions")

        try:
            from backend.analysis.ml_engine import MLEngine
            ml = MLEngine(df)
            ml_available = True
        except Exception as e:
            st.error(f"ML engine error: {e}")
            ml_available = False

        if ml_available:
            tab1, tab2, tab3, tab4 = st.tabs(["📈 Regression", "🏷 Classification", "🔵 Clustering", "🔮 Forecasting"])

            with tab1:
                st.markdown("Predict a **numeric** value from other columns")
                c1, c2 = st.columns(2)
                tgt = c1.selectbox("Target (predict this)", num_cols, key="rt")
                feats = c2.multiselect("Features (optional — leave empty for auto)", [c for c in num_cols if c != tgt], key="rf")
                if st.button("▶ Run Regression", key="rb", use_container_width=True):
                    with st.spinner("Training 4 models..."):
                        res = ml.run_regression(tgt, feats or None)
                    if "error" in res:
                        st.error(res["error"])
                    else:
                        st.success(f"🏆 Best: **{res['best_model']}** — R² = `{res['best_r2']}`")
                        st.caption(res.get("interpretation",""))
                        # Model comparison
                        mr = res.get("model_results",{})
                        rows = [{"Model":m, "R²":v.get("r2","—"), "RMSE":v.get("rmse","—"), "MAE":v.get("mae","—")} for m,v in mr.items() if "error" not in v]
                        if rows: st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                        # Feature importance chart
                        fi = res.get("feature_importance",{})
                        if fi:
                            st.markdown("**Feature Importance:**")
                            fi_s = pd.Series(fi).sort_values()
                            fig, ax = dark_fig(8, max(3, len(fi_s)*0.4))
                            ax.barh(fi_s.index, fi_s.values, color="#58a6ff")
                            for i, v in enumerate(fi_s.values):
                                ax.text(v+0.001, i, f"{v:.3f}", va="center", color="#8b949e", fontsize=9)
                            fig.tight_layout(); st.pyplot(fig); plt.close(fig)
                        # Sample predictions
                        sp = res.get("sample_predictions",[])
                        if sp:
                            st.markdown("**Sample Predictions:**")
                            st.dataframe(pd.DataFrame(sp), use_container_width=True, hide_index=True)

            with tab2:
                st.markdown("Predict a **category** from other columns")
                c1, c2 = st.columns(2)
                tgt_c = c1.selectbox("Target (classify this)", df.columns.tolist(), key="ct")
                feats_c = c2.multiselect("Features", [c for c in num_cols if c != tgt_c], key="cf")
                if st.button("▶ Run Classification", key="cb", use_container_width=True):
                    with st.spinner("Training classifiers..."):
                        res = ml.run_classification(tgt_c, feats_c or None)
                    if "error" in res:
                        st.error(res["error"])
                    else:
                        st.success(f"🏆 Best: **{res['best_model']}** — **{res['best_accuracy']}%** accuracy")
                        st.caption(res.get("interpretation",""))
                        mr = res.get("model_results",{})
                        rows = [{"Model":m, "Accuracy %":v.get("accuracy_pct","—")} for m,v in mr.items() if "error" not in v]
                        if rows: st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                        fi = res.get("feature_importance",{})
                        if fi:
                            fi_s = pd.Series(fi).sort_values()
                            fig, ax = dark_fig(8, max(3, len(fi_s)*0.4))
                            ax.barh(fi_s.index, fi_s.values, color="#bc8cff")
                            fig.tight_layout(); st.pyplot(fig); plt.close(fig)

            with tab3:
                st.markdown("Find **natural groups** in your data")
                c1, c2 = st.columns(2)
                n_c = c1.slider("Clusters (0 = auto detect)", 0, 10, 0)
                feat_c = c2.multiselect("Features", num_cols, default=num_cols[:min(4,len(num_cols))], key="clf")
                if st.button("▶ Find Clusters", key="clb", use_container_width=True):
                    with st.spinner("Running K-Means..."):
                        res = ml.run_clustering(n_c or None, feat_c or None)
                    if "error" in res:
                        st.error(res["error"])
                    else:
                        sil = res.get("silhouette_score",0)
                        qual = res.get("quality","")
                        st.success(f"🎯 {res['n_clusters']} clusters found — Silhouette: `{sil}` ({qual})")
                        st.caption(res.get("interpretation",""))
                        cols_c = st.columns(min(res["n_clusters"], 3))
                        for i, (name, profile) in enumerate(res.get("cluster_profiles",{}).items()):
                            with cols_c[i % len(cols_c)]:
                                st.markdown(f"**{name}**")
                                st.markdown(f"`{profile['size']} records ({profile['pct']}%)`")
                                means = profile.get("means",{})
                                for col_n, val in list(means.items())[:4]:
                                    st.markdown(f"<small style='color:#8b949e'>{col_n}: <strong style='color:#58a6ff'>{val}</strong></small>", unsafe_allow_html=True)

            with tab4:
                st.markdown("Predict **future values** (trend-based forecasting)")
                c1, c2 = st.columns(2)
                tgt_f = c1.selectbox("Column to forecast", num_cols, key="ft")
                periods = c2.slider("Forecast periods", 3, 24, 6)
                if st.button("▶ Forecast", key="fb", use_container_width=True):
                    with st.spinner("Forecasting..."):
                        res = ml.run_forecasting(tgt_f, periods)
                    if "error" in res:
                        st.error(res["error"])
                    else:
                        st.success(f"{res['trend_direction']} | R²={res['r2_score']}")
                        st.caption(res.get("interpretation",""))
                        forecast = res.get("forecast",[])
                        historical = res.get("historical_values",[])
                        # Chart
                        fig, ax = dark_fig(10, 4)
                        x_hist = list(range(len(historical)))
                        x_fore = list(range(len(historical), len(historical)+len(forecast)))
                        ax.plot(x_hist, historical, color="#58a6ff", linewidth=2, label="Historical")
                        ax.plot(x_fore, forecast, color="#3fb950", linewidth=2.5, linestyle="--", label="Forecast", marker="o", markersize=5)
                        ax.axvline(x=len(historical)-1, color="#d29922", linestyle=":", alpha=0.7)
                        ax.legend(framealpha=0.3, labelcolor="#c9d1d9")
                        ax.set_title(f"Forecast: {tgt_f}", color="#e6edf3")
                        fig.tight_layout(); st.pyplot(fig); plt.close(fig)
                        # Forecast values
                        fc_cols = st.columns(min(len(forecast), 6))
                        for i, (val, col) in enumerate(zip(forecast, fc_cols)):
                            col.metric(f"Period {i+1}", val)

    # ── AI CHAT ───────────────────────────────────────
    elif page == "💬 AI Chat":
        st.markdown("## 💬 AI Data Analyst")
        st.caption("Powered by Groq Llama 3.3 70B — Ask anything in Hinglish!")

        context = f"""Dataset: {st.session_state.filename}
Shape: {sh.get('rows',0):,} rows × {sh.get('columns',0)} cols
Columns: {', '.join(df.columns.tolist())}
Numeric: {', '.join(num_cols)}
Categorical: {', '.join(cat_cols)}
Quality Score: {qr.get('quality_score',0)}/100
Missing: {ov.get('missing',{}).get('total_missing_cells',0)}
Goal: {st.session_state.goal_question or 'General analysis'}
Sample Data:\n{df.head(4).to_string()}
Key Stats:\n""" + "\n".join([f"  {c}: mean={s.get('mean')}, std={s.get('std')}, outliers={s.get('outliers',{}).get('count',0)}" for c,s in list(ns.items())[:5]])

        system = f"""You are DataMind AI — expert data analyst.
{context}
Rules:
- Answer in Hinglish (Hindi+English mix)
- Use specific numbers from the data
- Use markdown formatting (bold, bullets)
- Be actionable and insightful"""

        # Quick action buttons
        st.markdown("**⚡ Quick Questions:**")
        qc = st.columns(5)
        quick = None
        if qc[0].button("📊 Summary"): quick = "Is dataset ka complete summary do — key numbers ke saath"
        if qc[1].button("💡 Insights"): quick = "Sabse important 5 insights kya hain is data mein?"
        if qc[2].button("⚠️ Issues"): quick = "Data quality issues kya hain aur kaise fix karein?"
        if qc[3].button("🎯 Actions"): quick = "Top 3 actionable recommendations do business ke liye"
        if qc[4].button("🤖 ML Suggest"): quick = "Is dataset ke liye best ML models suggest karo"

        # Chat display
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"], avatar="👤" if msg["role"]=="user" else "🤖"):
                st.markdown(msg["content"])

        # Input
        user_in = st.chat_input("Kuch bhi poochho is dataset ke baare mein...")
        if quick: user_in = quick

        if user_in:
            st.session_state.chat_history.append({"role":"user","content":user_in})
            with st.chat_message("user", avatar="👤"):
                st.markdown(user_in)
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Thinking..."):
                    reply = ask_ai(user_in, system, st.session_state.chat_history[:-1])
                st.markdown(reply)
            st.session_state.chat_history.append({"role":"assistant","content":reply})

        if st.session_state.chat_history:
            if st.button("🗑 Clear Chat", use_container_width=False):
                st.session_state.chat_history = []
                st.rerun()

    # ── INSIGHTS ──────────────────────────────────────
    elif page == "📢 Insights":
        st.markdown("## 📢 AI Executive Summary")
        st.caption("AI-generated insights based on your data")

        context = f"""Dataset: {st.session_state.filename} ({sh.get('rows',0)} rows × {sh.get('columns',0)} cols)
Goal: {st.session_state.goal_question or 'General data analysis'}
Quality Score: {qr.get('quality_score',0)}/100
Numeric columns: {', '.join(num_cols)}
Categorical columns: {', '.join(cat_cols)}
Stats:\n""" + "\n".join([f"  {c}: mean={s.get('mean')}, std={s.get('std')}, min={s.get('min')}, max={s.get('max')}, outliers={s.get('outliers',{}).get('count',0)}" for c,s in list(ns.items())[:6]]) + f"\nStrong correlations: {json.dumps(corr.get('strong_pairs',[])[:4])}"

        if st.button("🚀 Generate AI Insights", use_container_width=True, type="primary"):
            prompt = f"""{context}

Generate comprehensive executive summary. Return ONLY this JSON:
{{"headline":"one powerful sentence with the key finding and actual numbers","overview":"2-3 sentences about what this dataset tells us","key_findings":[{{"finding":"specific insight with real numbers","significance":"why this matters for business","type":"positive/negative/neutral"}}],"data_story":"4-5 sentence narrative telling the story of this data","anomalies":["specific unusual patterns with numbers"],"recommendations":["top 3 immediate actions"]}}

Use REAL numbers from the stats. Be specific. Write like McKinsey analyst."""

            with st.spinner("🤖 Generating insights..."):
                result = ask_ai_json(prompt)

            if "_raw" in result:
                st.markdown(result["_raw"])
            else:
                # Headline
                st.markdown(f"<h2 style='color:#58a6ff;border-bottom:2px solid #21262d;padding-bottom:10px'>{result.get('headline','')}</h2>", unsafe_allow_html=True)
                # Overview
                st.markdown(f"<p style='color:#c9d1d9;font-size:16px;font-style:italic'>{result.get('overview','')}</p>", unsafe_allow_html=True)

                st.markdown("---")
                col1, col2 = st.columns([1.2, 1])

                with col1:
                    st.markdown("### 🔑 Key Findings")
                    type_colors = {"positive": "#3fb950", "negative": "#f85149", "neutral": "#58a6ff"}
                    for f in result.get("key_findings", []):
                        color = type_colors.get(f.get("type","neutral"), "#58a6ff")
                        st.markdown(f"""<div class='insight-box' style='border-left-color:{color}'>
                        <strong style='color:{color}'>{f.get('finding','')}</strong>
                        <br><small style='color:#8b949e'>{f.get('significance','')}</small>
                        </div>""", unsafe_allow_html=True)

                with col2:
                    st.markdown("### 📖 Data Story")
                    st.markdown(f"<p style='color:#c9d1d9;line-height:1.7'>{result.get('data_story','')}</p>", unsafe_allow_html=True)

                    if result.get("anomalies"):
                        st.markdown("### ⚠️ Anomalies")
                        for a in result["anomalies"]:
                            st.markdown(f'<div class="warn-box"><span style="color:#d29922">⚠️ {a}</span></div>', unsafe_allow_html=True)

                if result.get("recommendations"):
                    st.markdown("### 💡 Quick Recommendations")
                    for i, rec in enumerate(result["recommendations"], 1):
                        st.markdown(f'<div class="action-box"><strong style="color:#3fb950">{i}.</strong> <span style="color:#c9d1d9">{rec}</span></div>', unsafe_allow_html=True)

    # ── RECOMMENDATIONS ───────────────────────────────
    elif page == "🎯 Recommendations":
        st.markdown("## 🎯 Action Recommendations")
        st.caption("AI-powered prioritized action items")

        context = f"""Dataset: {st.session_state.filename}
Goal: {st.session_state.goal_question or 'General analysis'}
Shape: {sh.get('rows',0)} rows × {sh.get('columns',0)} cols
Quality: {qr.get('quality_score',0)}/100
Issues: {json.dumps([i.get('message','') for i in qr.get('issues',[])[:4]])}
Stats:\n""" + "\n".join([f"  {c}: mean={s.get('mean')}, outliers={s.get('outliers',{}).get('count',0)}" for c,s in list(ns.items())[:5]])

        if st.button("🚀 Generate Recommendations", use_container_width=True, type="primary"):
            prompt = f"""{context}

Generate specific actionable recommendations. Return ONLY this JSON:
{{"immediate_actions":[{{"action":"specific action to take NOW","reason":"exact data evidence with numbers","impact":"high/medium/low","effort":"low/medium/high","timeline":"today/this week/this month","metric":"how to measure success"}}],"strategic_recommendations":[{{"recommendation":"longer term strategic move","business_value":"quantified expected benefit","data_evidence":"what in the data supports this"}}],"data_improvements":[{{"improvement":"data collection gap","why":"what analysis this enables"}}],"watch_out":[{{"risk":"specific risk to monitor","indicator":"early warning sign"}}]}}

Be SPECIFIC. Reference actual column names and numbers. Think like a senior consultant."""

            with st.spinner("🤖 Generating recommendations..."):
                result = ask_ai_json(prompt)

            if "_raw" in result:
                st.markdown(result["_raw"])
            else:
                st.markdown("### ⚡ Immediate Actions")
                impact_emoji = {"high":"🔴","medium":"🟡","low":"🟢"}
                for i, action in enumerate(result.get("immediate_actions",[]), 1):
                    imp = action.get("impact","medium").lower()
                    eff = action.get("effort","medium").lower()
                    with st.expander(f"{impact_emoji.get(imp,'⚪')} {i}. {action.get('action','')}"):
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Impact", action.get("impact","—").title())
                        c2.metric("Effort", action.get("effort","—").title())
                        c3.metric("Timeline", action.get("timeline","—"))
                        st.markdown(f"**📊 Evidence:** {action.get('reason','')}")
                        st.markdown(f"**📏 Measure by:** {action.get('metric','')}")

                col1, col2 = st.columns(2)
                with col1:
                    if result.get("strategic_recommendations"):
                        st.markdown("### 🎯 Strategic")
                        for rec in result["strategic_recommendations"]:
                            st.markdown(f'<div class="action-box"><strong style="color:#3fb950">{rec.get("recommendation","")}</strong><br><small style="color:#8b949e">{rec.get("business_value","")}</small><br><small style="color:#58a6ff">{rec.get("data_evidence","")}</small></div>', unsafe_allow_html=True)

                with col2:
                    if result.get("watch_out"):
                        st.markdown("### 👀 Watch Out For")
                        for w in result["watch_out"]:
                            st.markdown(f'<div class="warn-box"><strong style="color:#d29922">{w.get("risk","")}</strong><br><small style="color:#8b949e">Indicator: {w.get("indicator","")}</small></div>', unsafe_allow_html=True)

                if result.get("data_improvements"):
                    st.markdown("### 📈 Improve Your Data")
                    for imp in result["data_improvements"]:
                        st.info(f"**{imp.get('improvement','')}** — {imp.get('why','')}")

    # ── PREVIEW ───────────────────────────────────────
    elif page == "📋 Data Preview":
        st.markdown("## 📋 Data Preview")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Rows", f"{len(df):,}")
        c2.metric("Total Columns", len(df.columns))
        c3.metric("Memory", f"{df.memory_usage(deep=True).sum()/1024:.1f} KB")
        st.markdown("---")
        n_rows = st.slider("Rows to show", 10, min(500, len(df)), 50)
        col_filter = st.multiselect("Filter columns", df.columns.tolist(), default=df.columns.tolist())
        if col_filter:
            st.dataframe(df[col_filter].head(n_rows), use_container_width=True)
        st.markdown("**Column Info:**")
        info_data = []
        for col in df.columns:
            info_data.append({
                "Column": col,
                "Type": str(df[col].dtype),
                "Non-Null": int(df[col].notna().sum()),
                "Null": int(df[col].isna().sum()),
                "Unique": int(df[col].nunique()),
                "Sample": str(df[col].dropna().iloc[0]) if len(df[col].dropna()) > 0 else "—"
            })
        st.dataframe(pd.DataFrame(info_data), use_container_width=True, hide_index=True)