"""
DataMind Pro v3 — Streamlit
Same feel as Flask version — dark theme, tabs, chatbot
"""
import streamlit as st
import pandas as pd
import numpy as np
import sys, os, io, json, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from dotenv import load_dotenv; load_dotenv(override=True)
except: pass

st.set_page_config(page_title="DataMind Pro ⚡", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

# ── FULL CSS — exact Flask feel ──────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
* { box-sizing: border-box; }
html, body, .stApp { background: #0d1117 !important; color: #e6edf3 !important; font-family: 'Syne', sans-serif !important; }
[data-testid="stSidebar"] { display: none !important; }
[data-testid="stHeader"] { background: #0d1117 !important; border-bottom: 1px solid #21262d; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }
h1,h2,h3,h4,h5 { font-family: 'Syne', sans-serif !important; color: #e6edf3 !important; }

/* ── TOPBAR ── */
.topbar {
  background: #010409; border-bottom: 1px solid #21262d;
  padding: 0 28px; height: 56px;
  display: flex; align-items: center; justify-content: space-between;
  position: sticky; top: 0; z-index: 999;
}
.logo { display: flex; align-items: center; gap: 10px; font-size: 20px; font-weight: 800; }
.logo em { color: #58a6ff; font-style: normal; }
.logo sup { font-size: 10px; color: #bc8cff; }
.ds-badge {
  background: rgba(88,166,255,.1); border: 1px solid rgba(88,166,255,.2);
  color: #58a6ff; border-radius: 20px; padding: 4px 14px; font-size: 12px;
}

/* ── NAV TABS ── */
.nav-tabs {
  background: #010409; border-bottom: 1px solid #21262d;
  padding: 0 20px; display: flex; gap: 2px; overflow-x: auto;
}
.nav-tab {
  padding: 12px 18px; font-size: 13px; font-weight: 600; cursor: pointer;
  border: none; background: transparent; color: #8b949e;
  border-bottom: 2px solid transparent; white-space: nowrap;
  font-family: 'Syne', sans-serif; transition: all .2s;
}
.nav-tab:hover { color: #e6edf3 !important; }
.nav-tab.active { color: #58a6ff !important; border-bottom-color: #58a6ff !important; }
.nav-tab.active-green { color: #3fb950 !important; border-bottom-color: #3fb950 !important; }
.nav-tab.active-purple { color: #bc8cff !important; border-bottom-color: #bc8cff !important; }

/* ── LAYOUT ── */
.app-body { display: flex; height: calc(100vh - 97px); overflow: hidden; }
.main-panel { flex: 1; overflow-y: auto; padding: 24px 28px; }
.chat-panel {
  width: 320px; background: #010409; border-left: 1px solid #21262d;
  display: flex; flex-direction: column; flex-shrink: 0;
}

/* ── CARDS ── */
.card {
  background: #161b22; border: 1px solid #21262d; border-radius: 12px;
  padding: 20px; margin-bottom: 16px;
}
.card-title { font-size: 14px; font-weight: 700; color: #8b949e; text-transform: uppercase; letter-spacing: .05em; margin-bottom: 14px; }
.metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin-bottom: 20px; }
.metric-card {
  background: #161b22; border: 1px solid #21262d; border-radius: 10px;
  padding: 16px; text-align: center;
}
.metric-val { font-size: 26px; font-weight: 800; color: #58a6ff; font-family: 'JetBrains Mono', monospace; }
.metric-lbl { font-size: 11px; color: #8b949e; margin-top: 4px; text-transform: uppercase; letter-spacing: .05em; }
.metric-green .metric-val { color: #3fb950; }
.metric-orange .metric-val { color: #d29922; }
.metric-red .metric-val { color: #f85149; }
.metric-purple .metric-val { color: #bc8cff; }

/* ── STAT TABLE ── */
.stat-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.stat-table th { background: #0d1117; color: #58a6ff; padding: 10px 12px; text-align: left; font-size: 11px; text-transform: uppercase; letter-spacing: .05em; }
.stat-table td { padding: 9px 12px; border-bottom: 1px solid #21262d; color: #c9d1d9; font-family: 'JetBrains Mono', monospace; font-size: 12px; }
.stat-table tr:hover td { background: rgba(88,166,255,.04); }

/* ── FILL BAR ── */
.fill-bar { background: #21262d; border-radius: 4px; height: 6px; margin-top: 4px; }
.fill-inner { height: 6px; border-radius: 4px; background: linear-gradient(90deg,#58a6ff,#bc8cff); }

/* ── BUTTONS ── */
.btn { display: inline-flex; align-items: center; gap: 8px; padding: 10px 20px;
  border-radius: 9px; font-weight: 700; font-size: 13px; cursor: pointer;
  border: none; font-family: 'Syne', sans-serif; transition: all .2s; }
.btn-primary { background: linear-gradient(135deg,#388bfd,#58a6ff); color: #fff; }
.btn-primary:hover { background: linear-gradient(135deg,#58a6ff,#79c0ff); }
.btn-green { background: linear-gradient(135deg,#238636,#3fb950); color: #fff; }
.btn-ghost { background: transparent; border: 1px solid #21262d; color: #8b949e; }
.btn-ghost:hover { border-color: #58a6ff; color: #58a6ff; }

/* ── UPLOAD AREA ── */
.upload-zone {
  border: 2px dashed #21262d; border-radius: 14px;
  padding: 40px; text-align: center; cursor: pointer;
  transition: all .3s; background: rgba(88,166,255,.02);
}
.upload-zone:hover { border-color: #58a6ff; background: rgba(88,166,255,.05); }
.upload-icon { font-size: 48px; margin-bottom: 12px; }
.upload-title { font-size: 18px; font-weight: 700; color: #e6edf3; margin-bottom: 6px; }
.upload-sub { color: #8b949e; font-size: 13px; }

/* ── GOAL CARDS ── */
.goal-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin: 20px 0; }
.goal-card {
  background: #161b22; border: 2px solid #21262d; border-radius: 12px;
  padding: 20px; cursor: pointer; text-align: center; transition: all .2s;
}
.goal-card:hover { border-color: #388bfd; background: rgba(88,166,255,.05); }
.goal-card.selected { border-color: #58a6ff; background: rgba(88,166,255,.08); }
.goal-icon { font-size: 32px; margin-bottom: 8px; }
.goal-title { font-weight: 700; font-size: 14px; color: #e6edf3; }
.goal-sub { font-size: 12px; color: #8b949e; margin-top: 4px; }

/* ── CHART TABS ── */
.chart-tabs { display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }
.chart-tab {
  padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 600;
  cursor: pointer; border: 1px solid #21262d; background: transparent; color: #8b949e;
  font-family: 'Syne', sans-serif;
}
.chart-tab.active { background: rgba(88,166,255,.1); border-color: #58a6ff; color: #58a6ff; }

/* ── INSIGHT CARDS ── */
.insight-card { background: #0d1117; border-left: 3px solid #58a6ff; padding: 14px 16px; border-radius: 0 10px 10px 0; margin: 8px 0; }
.insight-pos { border-left-color: #3fb950; }
.insight-neg { border-left-color: #f85149; }
.insight-warn { border-left-color: #d29922; }
.insight-title { font-weight: 700; color: #e6edf3; font-size: 14px; margin-bottom: 4px; }
.insight-sub { color: #8b949e; font-size: 12px; }

/* ── ACTION CARDS ── */
.action-card {
  background: #161b22; border: 1px solid #21262d; border-radius: 10px;
  padding: 14px 16px; margin: 8px 0;
  display: flex; gap: 12px; align-items: flex-start;
}
.action-num {
  background: linear-gradient(135deg,#388bfd,#58a6ff);
  color: #fff; font-weight: 800; width: 28px; height: 28px;
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-size: 12px; flex-shrink: 0;
}
.impact-high { color: #f85149; }
.impact-med { color: #d29922; }
.impact-low { color: #3fb950; }

/* ── CHATBOT ── */
.chat-head {
  padding: 14px 16px; border-bottom: 1px solid #21262d;
  display: flex; align-items: center; gap: 10px;
}
.chat-av {
  width: 32px; height: 32px; background: linear-gradient(135deg,#58a6ff,#bc8cff);
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-size: 16px;
}
.chat-name { font-weight: 700; font-size: 13px; color: #e6edf3; }
.chat-status { font-size: 11px; color: #3fb950; }
.chat-msgs { flex: 1; overflow-y: auto; padding: 12px; display: flex; flex-direction: column; gap: 8px; }
.chat-bubble { padding: 10px 12px; border-radius: 10px; font-size: 13px; line-height: 1.5; max-width: 95%; }
.chat-user-bubble { background: #1c2333; border: 1px solid rgba(88,166,255,.2); align-self: flex-end; color: #e6edf3; }
.chat-ai-bubble { background: #161b22; border: 1px solid #21262d; align-self: flex-start; color: #c9d1d9; }
.chat-pills { display: flex; flex-wrap: wrap; gap: 5px; padding: 8px 12px; border-top: 1px solid #21262d; }
.chat-pill {
  padding: 4px 10px; background: rgba(88,166,255,.08); border: 1px solid rgba(88,166,255,.15);
  border-radius: 12px; font-size: 11px; color: #58a6ff; cursor: pointer;
  font-family: 'Syne', sans-serif;
}
.chat-input-row { display: flex; gap: 8px; padding: 10px 12px; border-top: 1px solid #21262d; }

/* ── TRANSFORM ── */
.tf-grid { display: grid; grid-template-columns: repeat(2,1fr); gap: 14px; }
.tf-card { background: #0d1117; border: 1px solid #21262d; border-radius: 10px; padding: 16px; }
.tf-card h4 { font-size: 13px; font-weight: 700; color: #e6edf3; margin-bottom: 8px; }

/* ── QUALITY ── */
.q-issue { padding: 10px 14px; border-radius: 8px; margin: 6px 0; font-size: 13px; display: flex; align-items: center; gap: 10px; }
.q-critical { background: rgba(248,81,73,.08); border: 1px solid rgba(248,81,73,.2); color: #f85149; }
.q-warning { background: rgba(210,153,34,.08); border: 1px solid rgba(210,153,34,.2); color: #d29922; }
.q-info { background: rgba(88,166,255,.08); border: 1px solid rgba(88,166,255,.2); color: #58a6ff; }

/* ── ML ── */
.ml-result { background: #0d1117; border: 1px solid #21262d; border-radius: 10px; padding: 16px; margin-top: 12px; }
.ml-best { font-size: 18px; font-weight: 800; color: #3fb950; margin-bottom: 8px; }

/* ── STEP INDICATORS ── */
.steps { display: flex; align-items: center; gap: 0; }
.step { width: 30px; height: 30px; border-radius: 50%; border: 2px solid #21262d; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; color: #8b949e; }
.step.done { background: #238636; border-color: #3fb950; color: #fff; }
.step.active { background: #388bfd; border-color: #58a6ff; color: #fff; }
.step-line { width: 24px; height: 2px; background: #21262d; }
.step-line.done { background: #3fb950; }

/* Override streamlit elements */
.stFileUploader { background: transparent !important; }
.stFileUploader > div { background: #161b22 !important; border: 2px dashed #21262d !important; border-radius: 14px !important; }
.stFileUploader > div:hover { border-color: #58a6ff !important; }
.stTextInput > div > div > input { background: #161b22 !important; border: 1px solid #21262d !important; color: #e6edf3 !important; border-radius: 8px !important; font-family: 'Syne', sans-serif !important; }
.stSelectbox > div > div { background: #161b22 !important; border: 1px solid #21262d !important; color: #e6edf3 !important; border-radius: 8px !important; }
.stSelectbox svg { fill: #8b949e !important; }
.stMultiSelect > div { background: #161b22 !important; border: 1px solid #21262d !important; border-radius: 8px !important; }
.stSlider > div > div > div > div { background: #58a6ff !important; }
.stCheckbox > label > div { background: #161b22 !important; border-color: #21262d !important; }
div[data-testid="stDataFrame"] { background: #161b22; border: 1px solid #21262d; border-radius: 10px; overflow: hidden; }
.stAlert { border-radius: 10px !important; }
.stSpinner > div { border-top-color: #58a6ff !important; }
[data-testid="stChatInput"] { background: #161b22 !important; border-color: #21262d !important; color: #e6edf3 !important; }
[data-testid="stChatInput"] input { background: transparent !important; color: #e6edf3 !important; font-family: 'Syne', sans-serif !important; }
</style>
""", unsafe_allow_html=True)

PALETTE = ["#58a6ff","#bc8cff","#3fb950","#d29922","#f85149","#79c0ff","#ffa657","#ff7b72"]

# ── STATE ────────────────────────────────────────────
for k,v in {"df":None,"filename":None,"analysis":None,"goal_type":"custom","goal_question":"",
             "chat_history":[],"page":"home","ml_cache":{}}.items():
    if k not in st.session_state: st.session_state[k]=v

# ── AI ───────────────────────────────────────────────
def ask_ai(prompt, system="You are an expert data analyst. Be specific with numbers. Reply in Hinglish.", history=None):
    import requests
    key = os.getenv("GROQ_API_KEY","") or (st.secrets.get("GROQ_API_KEY","") if hasattr(st,"secrets") else "")
    if not key: return "⚠️ GROQ_API_KEY not set. Add in Streamlit Cloud → Secrets."
    msgs = [{"role":"system","content":system}]
    if history: msgs += [m for m in history[-8:] if m.get("role") in ("user","assistant")]
    msgs.append({"role":"user","content":prompt})
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},
            json={"model":"llama-3.3-70b-versatile","messages":msgs,"max_tokens":2000,"temperature":0.7},timeout=45)
        return r.json()["choices"][0]["message"]["content"] if r.status_code==200 else f"❌ API {r.status_code}"
    except Exception as e: return f"❌ {e}"

def ask_ai_json(prompt):
    r = ask_ai(prompt, "You are a data analyst. Return ONLY valid JSON, no markdown, no backticks.")
    try: return json.loads(r.replace("```json","").replace("```","").strip())
    except: return {"_raw":r}

# ── DATA LOAD ────────────────────────────────────────
def load_file(f):
    n = f.name.lower()
    if n.endswith(".csv"): return pd.read_csv(f)
    if n.endswith(".tsv"): return pd.read_csv(f,sep="\t")
    if n.endswith((".xlsx",".xls")): return pd.read_excel(f)
    if n.endswith(".json"): return pd.read_json(f)
    raise ValueError(f"Unsupported: {n}")

# ── EDA ──────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def run_eda(key, _df):
    try:
        from backend.analysis.eda_engine import EDAEngine
        return EDAEngine(_df).run_full_analysis()
    except: return _basic_eda(_df)

def _basic_eda(df):
    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    cat_cols = df.select_dtypes(include="object").columns.tolist()
    ns={}
    for c in num_cols:
        s=df[c].dropna()
        if not len(s): continue
        q1,q3=s.quantile(.25),s.quantile(.75); iqr=q3-q1
        ns[c]={"mean":round(float(s.mean()),2),"median":round(float(s.median()),2),"std":round(float(s.std()),2),
               "min":round(float(s.min()),2),"max":round(float(s.max()),2),
               "outliers":{"count":int(((s<q1-1.5*iqr)|(s>q3+1.5*iqr)).sum())},"skewness":round(float(s.skew()),3)}
    cs={}
    for c in cat_cols[:5]:
        vc=df[c].value_counts().head(6)
        cs[c]={"unique_values":int(df[c].nunique()),"value_counts":vc.to_dict()}
    pairs=[]
    if len(num_cols)>=2:
        cm=df[num_cols].corr()
        for i in range(len(num_cols)):
            for j in range(i+1,len(num_cols)):
                r=float(cm.iloc[i,j])
                if abs(r)>=.5: pairs.append({"col1":num_cols[i],"col2":num_cols[j],"pearson_r":round(r,3),"strength":"strong" if abs(r)>=.7 else "moderate"})
        pairs.sort(key=lambda x:abs(x["pearson_r"]),reverse=True)
    miss=int(df.isnull().sum().sum()); dups=int(df.duplicated().sum())
    score=100; issues=[]
    if miss>0:
        p=miss/(df.shape[0]*df.shape[1])*100; score-=min(30,int(p*3))
        issues.append({"severity":"warning","message":f"{miss} missing values ({p:.1f}%)"})
    if dups>0:
        score-=min(20,dups); issues.append({"severity":"warning","message":f"{dups} duplicate rows"})
    for c,s in ns.items():
        if s["outliers"]["count"]>len(df)*.05:
            issues.append({"severity":"info","message":f"{c}: {s['outliers']['count']} outliers detected"})
    return {"overview":{"shape":{"rows":len(df),"columns":len(df.columns)},
            "missing":{"total_missing_cells":miss},"duplicates":{"duplicate_rows":dups},
            "column_types":{"numeric":num_cols,"categorical":cat_cols}},
            "numeric_stats":ns,"categorical_stats":cs,
            "correlations":{"strong_pairs":pairs[:8]},
            "quality_report":{"quality_score":max(0,score),"issues":issues,
                             "recommendations":[],"total_issues":len(issues)}}

# ── CHART HELPERS ─────────────────────────────────────
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, seaborn as sns

def dfig(w=10,h=5):
    fig,ax=plt.subplots(figsize=(w,h))
    fig.patch.set_facecolor("#0d1117"); ax.set_facecolor("#161b22")
    ax.tick_params(colors="#8b949e"); ax.xaxis.label.set_color("#c9d1d9"); ax.yaxis.label.set_color("#c9d1d9")
    ax.title.set_color("#e6edf3")
    for sp in ax.spines.values(): sp.set_edgecolor("#21262d")
    ax.grid(True,color="#21262d",linewidth=.5,alpha=.5)
    return fig,ax

# ════════════════════════════════════════════════════════
# TOPBAR
# ════════════════════════════════════════════════════════
df = st.session_state.df
a  = st.session_state.analysis or {}
ov = a.get("overview",{}); sh=ov.get("shape",{})
ns = a.get("numeric_stats",{}); cs=a.get("categorical_stats",{})
qr = a.get("quality_report",{}); corr=a.get("correlations",{})
num_cols = df.select_dtypes(include=np.number).columns.tolist() if df is not None else []
cat_cols = df.select_dtypes(include="object").columns.tolist() if df is not None else []

# Topbar HTML
ds_badge = f'<span class="ds-badge">📁 {st.session_state.filename} — {sh.get("rows",0):,} × {sh.get("columns",0)}</span>' if df is not None else ""
st.markdown(f"""
<div class="topbar">
  <div class="logo">⚡ Data<em>Mind</em> Pro <sup>v3</sup></div>
  {ds_badge}
  <div style="font-size:12px;color:#8b949e">Groq Llama 3.3 🟢</div>
</div>""", unsafe_allow_html=True)

# ── PAGE ROUTING ──────────────────────────────────────
if df is None:
    page = "home"
else:
    # Navigation tabs
    pages = ["📊 Overview","🧹 Clean","📈 Charts","🤖 ML","📢 Insights","🎯 Actions","📋 Preview"]
    if "nav_page" not in st.session_state: st.session_state.nav_page = "📊 Overview"

    cols = st.columns(len(pages)+1)
    for i,(pg,col) in enumerate(zip(pages,cols)):
        active = "active" if st.session_state.nav_page == pg else ""
        if col.button(pg, key=f"nav_{i}", use_container_width=True):
            st.session_state.nav_page = pg
            st.rerun()
    if cols[-1].button("↺ Reset", key="nav_reset"):
        for k in ["df","filename","analysis","chat_history","ml_cache"]:
            st.session_state[k] = None if k not in ["chat_history","ml_cache"] else ([] if k=="chat_history" else {})
        st.session_state.nav_page = "📊 Overview"
        st.rerun()
    page = st.session_state.nav_page

# ════════════════════════════════════════════════════════
# HOME — UPLOAD
# ════════════════════════════════════════════════════════
if df is None:
    left, right = st.columns([1.3, 1])
    with left:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h1 style='font-size:48px;font-weight:800'>Ask the <span style='color:#58a6ff'>Right Question</span></h1>", unsafe_allow_html=True)
        st.markdown("<p style='color:#8b949e;font-size:16px'>Insight without a clear question = wasted effort.</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # Goal cards
        st.markdown("**Select your analysis goal:**")
        goals = [("🛒","Sales Performance","Revenue, targets, products"),
                 ("👥","Customer Analysis","Segments, churn, behaviour"),
                 ("🏢","HR / Workforce","Salary, performance, attrition"),
                 ("💰","Financial","Profit, costs, ROI"),
                 ("⚙️","Operations","Supply chain, delivery"),
                 ("🔬","Custom","Define your own")]
        g_cols = st.columns(3)
        for i,(icon,title,sub) in enumerate(goals):
            with g_cols[i%3]:
                selected = "selected" if st.session_state.goal_type == title else ""
                st.markdown(f'<div class="goal-card {selected}" onclick="">', unsafe_allow_html=True)
                if st.button(f"{icon} {title}", key=f"goal_{i}", use_container_width=True):
                    st.session_state.goal_type = title
                    st.rerun()
                st.markdown(f'<div style="font-size:11px;color:#8b949e;margin-top:-8px;margin-bottom:8px;text-align:center">{sub}</div>', unsafe_allow_html=True)

        q = st.text_input("", placeholder="e.g. Which products are underperforming this quarter?",
                          label_visibility="collapsed", key="goal_q_input")
        if q: st.session_state.goal_question = q

    with right:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("### 📂 Upload Your Dataset")
        uploaded = st.file_uploader("CSV • Excel • JSON • TSV", type=["csv","xlsx","xls","json","tsv"], label_visibility="collapsed")

        st.markdown("**Or try a sample:**")
        sc1,sc2,sc3 = st.columns(3)
        SAMPLES = {
            "sales":("sales.csv","month,product,category,sales,units,profit,region,target\nJan,Laptop,Electronics,145000,29,42000,North,130000\nJan,Phone,Electronics,89000,89,22000,South,80000\nFeb,Laptop,Electronics,167000,33,48000,North,150000\nFeb,Shoes,Apparel,41000,136,11000,South,38000\nMar,TV,Electronics,78000,15,18000,North,75000\nApr,Phone,Electronics,103000,103,26000,North,95000\nApr,Laptop,Electronics,188000,37,55000,South,170000\nMay,Laptop,Electronics,172000,34,50000,West,160000\nJun,TV,Electronics,101000,19,23000,North,95000\nJun,Laptop,Electronics,195000,39,57000,West,180000"),
            "hr":("hr.csv","id,name,department,age,salary,experience,rating,city,gender,promoted\nE001,Rahul,Engineering,28,75000,4,4.2,Delhi,M,No\nE002,Priya,Marketing,32,65000,7,4.5,Mumbai,F,Yes\nE003,Amit,Engineering,35,92000,10,4.8,Bangalore,M,Yes\nE004,Sneha,HR,27,48000,3,3.9,Delhi,F,No\nE005,Vikram,Engineering,30,82000,6,4.3,Hyderabad,M,No\nE006,Rajesh,Finance,40,110000,15,4.6,Mumbai,M,Yes\nE007,Kavita,Engineering,26,68000,2,3.8,Bangalore,F,No\nE008,Deepa,Finance,37,98000,12,4.7,Hyderabad,F,Yes\nE009,Nitin,Engineering,31,85000,7,4.4,Delhi,M,No\nE010,Meera,Finance,34,88000,9,4.2,Chennai,F,Yes"),
            "ecomm":("ecomm.csv","order_id,product,category,price,qty,discount,rating,delivery_days,returned\nORD001,Earbuds,Electronics,2499,1,10,4.3,3,No\nORD002,Kurta,Clothing,899,2,5,4.1,5,No\nORD003,Python Book,Books,599,1,0,4.7,4,No\nORD004,Shoes,Footwear,3499,1,15,3.9,6,Yes\nORD005,Speaker,Electronics,1999,1,8,4.5,3,No\nORD006,Watch,Electronics,8999,1,12,4.6,3,Yes\nORD007,Yoga Mat,Sports,1499,1,0,4.4,5,No\nORD008,Formal Shoes,Footwear,2999,1,5,4.2,7,No\nORD009,Jeans,Clothing,1299,1,10,4.0,5,No\nORD010,Cricket Bat,Sports,2999,1,5,4.6,7,No"),
        }
        load_s = None
        with sc1:
            if st.button("🛒 Sales", use_container_width=True): load_s="sales"
        with sc2:
            if st.button("👥 HR", use_container_width=True): load_s="hr"
        with sc3:
            if st.button("📦 E-comm", use_container_width=True): load_s="ecomm"

        def process_df(dataframe, fname):
            st.session_state.df = dataframe
            st.session_state.filename = fname
            with st.spinner("⚡ Running analysis..."):
                st.session_state.analysis = run_eda(fname+str(dataframe.shape), dataframe)

        if load_s:
            fname, csv = SAMPLES[load_s]
            process_df(pd.read_csv(io.StringIO(csv)), fname)
            st.rerun()
        if uploaded:
            try:
                process_df(load_file(uploaded), uploaded.name)
                st.rerun()
            except Exception as e:
                st.error(f"❌ {e}")

# ════════════════════════════════════════════════════════
# ANALYSIS PAGES + CHATBOT
# ════════════════════════════════════════════════════════
else:
    main_col, chat_col = st.columns([3.2, 1])

    # ════════ CHAT PANEL ════════
    with chat_col:
        st.markdown("""
        <div style='background:#010409;border-left:1px solid #21262d;height:calc(100vh - 97px);display:flex;flex-direction:column;position:sticky;top:97px'>
        <div class='chat-head'>
          <div class='chat-av'>🤖</div>
          <div><div class='chat-name'>DataMind AI</div><div class='chat-status'>● Groq Llama 3.3</div></div>
        </div>
        </div>""", unsafe_allow_html=True)

        # Build context for AI
        ctx = f"""Dataset: {st.session_state.filename}
Shape: {sh.get('rows',0):,} rows × {sh.get('columns',0)} cols
Columns: {', '.join(df.columns.tolist())}
Numeric: {', '.join(num_cols)}
Quality: {qr.get('quality_score',0)}/100
Goal: {st.session_state.goal_question or 'General analysis'}
Sample:\n{df.head(3).to_string()}
Stats:\n"""+"\n".join([f"  {c}: mean={s.get('mean')}, std={s.get('std')}, outliers={s.get('outliers',{}).get('count',0)}" for c,s in list(ns.items())[:5]])

        system_prompt = f"""You are DataMind AI — expert data analyst assistant.
{ctx}
Rules: Reply in Hinglish (Hindi+English mix). Use specific numbers. Use markdown bold/bullets. Be actionable."""

        # Quick pills
        pills = ["📊 Summary", "💡 Insights", "🎯 Actions", "🤖 ML?"]
        pill_cols = st.columns(4)
        quick = None
        for i,(pill,col) in enumerate(zip(pills,pill_cols)):
            if col.button(pill, key=f"pill_{i}", use_container_width=True):
                quick = {"📊 Summary":"Dataset ka summary do — key numbers ke saath",
                         "💡 Insights":"Top 5 insights kya hain?",
                         "🎯 Actions":"Top 3 actions batao",
                         "🤖 ML?":"Best ML model suggest karo"}[pill]

        # Chat messages
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.chat_history[-12:]:
                if msg["role"] == "user":
                    st.markdown(f'<div class="chat-bubble chat-user-bubble">👤 {msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-bubble chat-ai-bubble">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

        # Input
        user_in = st.chat_input("Kuch bhi poochho...", key="chat_in")
        if quick: user_in = quick

        if user_in:
            st.session_state.chat_history.append({"role":"user","content":user_in})
            with st.spinner("🤖"):
                reply = ask_ai(user_in, system_prompt, st.session_state.chat_history[:-1])
            st.session_state.chat_history.append({"role":"assistant","content":reply})
            st.rerun()

        if st.session_state.chat_history:
            if st.button("🗑 Clear", key="clear_chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()

    # ════════ MAIN PANEL ════════
    with main_col:

        # ── OVERVIEW ─────────────────────────────────
        if page == "📊 Overview":
            score = qr.get("quality_score",0)
            score_col = "metric-green" if score>=80 else ("metric-orange" if score>=60 else "metric-red")

            # Metrics
            metrics_html = f"""<div class="metric-grid">
            <div class="metric-card"><div class="metric-val">{sh.get('rows',0):,}</div><div class="metric-lbl">Total Rows</div></div>
            <div class="metric-card metric-purple"><div class="metric-val">{sh.get('columns',0)}</div><div class="metric-lbl">Columns</div></div>
            <div class="metric-card {'metric-orange' if ov.get('missing',{}).get('total_missing_cells',0)>0 else 'metric-green'}"><div class="metric-val">{ov.get('missing',{}).get('total_missing_cells',0)}</div><div class="metric-lbl">Missing Values</div></div>
            <div class="metric-card {'metric-orange' if ov.get('duplicates',{}).get('duplicate_rows',0)>0 else 'metric-green'}"><div class="metric-val">{ov.get('duplicates',{}).get('duplicate_rows',0)}</div><div class="metric-lbl">Duplicates</div></div>
            <div class="metric-card"><div class="metric-val">{len(num_cols)}</div><div class="metric-lbl">Numeric Cols</div></div>
            <div class="metric-card {score_col}"><div class="metric-val">{score}</div><div class="metric-lbl">Quality /100</div></div>
            </div>"""
            st.markdown(metrics_html, unsafe_allow_html=True)

            col1, col2 = st.columns([1.6, 1])
            with col1:
                if ns:
                    st.markdown('<div class="card"><div class="card-title">📈 Statistical Summary</div>', unsafe_allow_html=True)
                    rows = [{"Column":c,"Mean":s.get("mean"),"Median":s.get("median"),"Std":s.get("std"),"Min":s.get("min"),"Max":s.get("max"),"Outliers":s.get("outliers",{}).get("count",0)} for c,s in ns.items()]
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=min(400, len(rows)*38+40))
                    st.markdown('</div>', unsafe_allow_html=True)

            with col2:
                strong = corr.get("strong_pairs",[])
                if strong:
                    st.markdown('<div class="card"><div class="card-title">🔗 Correlations</div>', unsafe_allow_html=True)
                    for p in strong[:6]:
                        r = p.get("pearson_r",0); pct = int(abs(r)*100)
                        color = "#3fb950" if r>0 else "#f85149"
                        st.markdown(f"""<div style='margin:8px 0'><div style='display:flex;justify-content:space-between;font-size:12px;margin-bottom:4px'><span style='color:#c9d1d9'>{p['col1'][:12]} ↔ {p['col2'][:12]}</span><span style='color:{color};font-weight:700'>{r}</span></div><div class='fill-bar'><div class='fill-inner' style='width:{pct}%;background:{color}'></div></div></div>""", unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                issues = qr.get("issues",[])
                if issues:
                    st.markdown('<div class="card"><div class="card-title">⚠️ Quality Issues</div>', unsafe_allow_html=True)
                    for issue in issues[:5]:
                        sev = issue.get("severity","info")
                        cls = f"q-{sev}"
                        icon = "🔴" if sev=="critical" else ("⚠️" if sev=="warning" else "ℹ️")
                        st.markdown(f'<div class="q-issue {cls}">{icon} {issue["message"]}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

            # Categorical charts
            if cs:
                st.markdown('<div class="card"><div class="card-title">🏷️ Categorical Overview</div>', unsafe_allow_html=True)
                cat_cols_show = list(cs.keys())[:4]
                ccols = st.columns(min(len(cat_cols_show),4))
                for i,(cname,cdata) in enumerate([(c,cs[c]) for c in cat_cols_show]):
                    with ccols[i]:
                        vc = cdata.get("value_counts",{})
                        if vc:
                            fig,ax = dfig(3.5,2.5)
                            items = list(vc.items())[:5]
                            ax.bar([str(x[0])[:10] for x in items],[x[1] for x in items],color=PALETTE[i%len(PALETTE)],alpha=.85)
                            ax.set_title(cname,fontsize=10,color="#e6edf3")
                            plt.xticks(rotation=25,ha="right",fontsize=7)
                            fig.tight_layout(); st.pyplot(fig); plt.close(fig)
                st.markdown('</div>', unsafe_allow_html=True)

        # ── CLEAN ─────────────────────────────────────
        elif page == "🧹 Clean":
            st.markdown('<div class="card"><div class="card-title">🧹 Step 3 — Clean & Transform</div>', unsafe_allow_html=True)
            c1,c2 = st.columns([1,1.8])
            with c1:
                op = st.selectbox("Operation", ["drop_duplicates","drop_column","fill_mean","fill_median","fill_zero","fill_unknown","normalize","rename_column","filter_rows","sort_asc","sort_desc","drop_na_rows"])
                col_sel = st.selectbox("Column", ["—"]+df.columns.tolist())
                extra = ""
                if op == "rename_column": extra = st.text_input("New name")
                if op == "filter_rows": extra = st.text_input("Contains value")
                if st.button("▶ Apply", use_container_width=True, type="primary"):
                    try:
                        ndf = df.copy(); msg=""
                        if op=="drop_duplicates": b=len(ndf); ndf=ndf.drop_duplicates(); msg=f"Removed {b-len(ndf)} duplicates"
                        elif op=="drop_column" and col_sel!="—": ndf=ndf.drop(columns=[col_sel]); msg=f"Dropped {col_sel}"
                        elif op=="fill_mean" and col_sel!="—": ndf[col_sel]=ndf[col_sel].fillna(ndf[col_sel].mean()); msg=f"Filled {col_sel} with mean"
                        elif op=="fill_median" and col_sel!="—": ndf[col_sel]=ndf[col_sel].fillna(ndf[col_sel].median()); msg=f"Filled {col_sel} with median"
                        elif op=="fill_zero" and col_sel!="—": ndf[col_sel]=ndf[col_sel].fillna(0); msg=f"Filled {col_sel} with 0"
                        elif op=="fill_unknown" and col_sel!="—": ndf[col_sel]=ndf[col_sel].fillna("Unknown"); msg=f"Filled {col_sel} with 'Unknown'"
                        elif op=="normalize" and col_sel!="—":
                            mn,mx=ndf[col_sel].min(),ndf[col_sel].max(); ndf[col_sel]=(ndf[col_sel]-mn)/(mx-mn+1e-9); msg=f"Normalized {col_sel}"
                        elif op=="rename_column" and col_sel!="—" and extra: ndf=ndf.rename(columns={col_sel:extra}); msg=f"Renamed → {extra}"
                        elif op=="filter_rows" and col_sel!="—" and extra:
                            b=len(ndf); ndf=ndf[ndf[col_sel].astype(str).str.contains(extra,na=False)]; msg=f"Filtered: {len(ndf)}/{b} rows"
                        elif op=="sort_asc" and col_sel!="—": ndf=ndf.sort_values(col_sel,ascending=True); msg=f"Sorted ↑ {col_sel}"
                        elif op=="sort_desc" and col_sel!="—": ndf=ndf.sort_values(col_sel,ascending=False); msg=f"Sorted ↓ {col_sel}"
                        elif op=="drop_na_rows": b=len(ndf); ndf=ndf.dropna(); msg=f"Dropped {b-len(ndf)} rows with NA"
                        if msg:
                            st.session_state.df=ndf
                            with st.spinner("Re-analyzing..."): st.session_state.analysis=run_eda(op+str(ndf.shape),ndf)
                            st.success(f"✅ {msg}"); st.rerun()
                        else: st.warning("Select a column first")
                    except Exception as e: st.error(f"❌ {e}")

            with c2:
                st.markdown(f"`{len(df):,} rows × {len(df.columns)} cols`")
                st.dataframe(df.head(30), use_container_width=True, hide_index=True, height=400)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── CHARTS ────────────────────────────────────
        elif page == "📈 Charts":
            st.markdown('<div class="card-title">📊 Step 4 — Analyze Patterns</div>', unsafe_allow_html=True)
            t1,t2,t3,t4,t5 = st.tabs(["📊 Distributions","🔗 Heatmap","📦 Box Plots","🔵 Scatter","🛠 Custom"])

            with t1:
                if num_cols:
                    sel = st.multiselect("Columns",num_cols,default=num_cols[:min(4,len(num_cols))],key="d_sel")
                    if sel:
                        n=len(sel); fig,axes=plt.subplots(1,n,figsize=(5*n,4)); fig.patch.set_facecolor("#0d1117")
                        if n==1: axes=[axes]
                        for i,c in enumerate(sel):
                            axes[i].set_facecolor("#161b22"); data=df[c].dropna()
                            axes[i].hist(data,bins=25,color=PALETTE[i%len(PALETTE)],alpha=.85,edgecolor="none")
                            axes[i].set_title(c,color="#e6edf3",fontsize=11)
                            axes[i].tick_params(colors="#8b949e")
                            for sp in axes[i].spines.values(): sp.set_edgecolor("#21262d")
                        fig.tight_layout(); st.pyplot(fig); plt.close(fig)

            with t2:
                if len(num_cols)>=2:
                    sel2=st.multiselect("Columns",num_cols,default=num_cols[:min(8,len(num_cols))],key="hm_sel")
                    if len(sel2)>=2:
                        cm=df[sel2].corr(); fig,ax=plt.subplots(figsize=(max(6,len(sel2)*1.2),max(5,len(sel2))))
                        fig.patch.set_facecolor("#0d1117"); ax.set_facecolor("#161b22")
                        sns.heatmap(cm,annot=True,fmt=".2f",cmap="coolwarm",center=0,ax=ax,linewidths=.5,linecolor="#21262d",cbar_kws={"shrink":.8})
                        ax.tick_params(colors="#c9d1d9",labelsize=9); ax.set_title("Correlation Heatmap",color="#e6edf3")
                        fig.tight_layout(); st.pyplot(fig); plt.close(fig)

            with t3:
                if num_cols:
                    sel3=st.multiselect("Columns",num_cols,default=num_cols[:min(4,len(num_cols))],key="bp_sel")
                    if sel3:
                        n=len(sel3); fig,axes=plt.subplots(1,n,figsize=(4*n,5)); fig.patch.set_facecolor("#0d1117")
                        if n==1: axes=[axes]
                        for i,c in enumerate(sel3):
                            axes[i].set_facecolor("#161b22")
                            bp=axes[i].boxplot([df[c].dropna()],patch_artist=True,
                                medianprops={"color":"#3fb950","linewidth":2.5},
                                whiskerprops={"color":"#8b949e"},capprops={"color":"#8b949e"},
                                flierprops={"marker":"o","markersize":3,"alpha":.4,"markerfacecolor":PALETTE[i%len(PALETTE)]})
                            bp["boxes"][0].set(facecolor="#58a6ff22",edgecolor="#58a6ff")
                            axes[i].set_title(c,color="#e6edf3"); axes[i].set_xticks([])
                            axes[i].tick_params(colors="#8b949e")
                            for sp in axes[i].spines.values(): sp.set_edgecolor("#21262d")
                        fig.tight_layout(); st.pyplot(fig); plt.close(fig)

            with t4:
                if len(num_cols)>=2:
                    c1,c2,c3=st.columns(3)
                    xc=c1.selectbox("X",num_cols,key="sc_x"); yc=c2.selectbox("Y",num_cols,index=min(1,len(num_cols)-1),key="sc_y")
                    hue=c3.selectbox("Color by",["None"]+cat_cols,key="sc_h")
                    fig,ax=dfig(9,5)
                    if hue!="None":
                        for i,cat in enumerate(df[hue].unique()[:8]):
                            m=df[hue]==cat; ax.scatter(df[m][xc],df[m][yc],label=str(cat),color=PALETTE[i%len(PALETTE)],alpha=.6,s=40)
                        ax.legend(framealpha=.3,labelcolor="#c9d1d9")
                    else: ax.scatter(df[xc],df[yc],color="#58a6ff",alpha=.5,s=30)
                    ax.set_xlabel(xc); ax.set_ylabel(yc); ax.set_title(f"{xc} vs {yc}",color="#e6edf3")
                    fig.tight_layout(); st.pyplot(fig); plt.close(fig)

            with t5:
                c1,c2,c3=st.columns(3)
                ct=c1.selectbox("Type",["bar","line","pie","histogram","area"],key="ct_type")
                xc=c2.selectbox("X/Category",df.columns.tolist(),key="ct_x")
                yc=c3.selectbox("Y/Value",["count"]+num_cols,key="ct_y")
                if st.button("⚡ Generate Chart",use_container_width=True):
                    try:
                        fig,ax=dfig(10,5)
                        if ct=="bar":
                            data=(df.groupby(xc)[yc].sum() if yc!="count" else df[xc].value_counts()).sort_values(ascending=False).head(12)
                            ax.bar(data.index.astype(str),data.values,color=[PALETTE[i%len(PALETTE)] for i in range(len(data))])
                            plt.xticks(rotation=30,ha="right")
                        elif ct=="line":
                            yd=df[yc] if yc!="count" else df[xc].value_counts().sort_index()
                            ax.plot(range(len(yd)),yd.values,color="#58a6ff",linewidth=2.5)
                            ax.fill_between(range(len(yd)),yd.values,alpha=.1,color="#58a6ff")
                        elif ct=="pie":
                            vc=df[xc].value_counts().head(7)
                            w,t,at=ax.pie(vc.values,labels=vc.index,colors=PALETTE[:len(vc)],autopct="%1.1f%%",pctdistance=.75,wedgeprops={"edgecolor":"#0d1117","linewidth":2})
                            for tx in t: tx.set_color("#c9d1d9")
                            for tx in at: tx.set_color("#0d1117")
                        elif ct=="histogram":
                            ch=yc if yc!="count" else xc; ax.hist(df[ch].dropna(),bins=30,color="#58a6ff",alpha=.85,edgecolor="none"); ax.set_xlabel(ch)
                        elif ct=="area":
                            yd=df[yc] if yc!="count" else df[xc].value_counts().sort_index()
                            ax.fill_between(range(len(yd)),yd.values,alpha=.4,color="#58a6ff")
                            ax.plot(range(len(yd)),yd.values,color="#58a6ff",linewidth=2)
                        ax.set_title(f"{ct.title()} — {xc}",color="#e6edf3",fontsize=13)
                        fig.tight_layout(); st.pyplot(fig); plt.close(fig)
                    except Exception as e: st.error(f"Chart error: {e}")

        # ── ML ────────────────────────────────────────
        elif page == "🤖 ML":
            st.markdown('<div class="card-title">🤖 ML Predictions</div>', unsafe_allow_html=True)
            try:
                from backend.analysis.ml_engine import MLEngine
                ml=MLEngine(df)
                t1,t2,t3,t4=st.tabs(["📈 Regression","🏷 Classification","🔵 Clustering","🔮 Forecasting"])

                with t1:
                    c1,c2=st.columns(2)
                    tgt=c1.selectbox("Target (numeric)",num_cols,key="r_t")
                    feats=c2.multiselect("Features (empty=auto)",[c for c in num_cols if c!=tgt],key="r_f")
                    if st.button("▶ Run Regression",use_container_width=True,key="r_btn"):
                        with st.spinner("Training 4 models..."): res=ml.run_regression(tgt,feats or None)
                        if "error" in res: st.error(res["error"])
                        else:
                            st.markdown(f'<div class="ml-result"><div class="ml-best">🏆 {res["best_model"]} — R²={res["best_r2"]}</div><div style="color:#8b949e;font-size:12px">{res.get("interpretation","")}</div></div>', unsafe_allow_html=True)
                            mr=res.get("model_results",{})
                            rows=[{"Model":m,"R²":v.get("r2","—"),"RMSE":v.get("rmse","—"),"MAE":v.get("mae","—")} for m,v in mr.items() if "error" not in v]
                            if rows: st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
                            fi=res.get("feature_importance",{})
                            if fi:
                                fi_s=pd.Series(fi).sort_values()
                                fig,ax=dfig(7,max(3,len(fi_s)*.4))
                                ax.barh(fi_s.index,fi_s.values,color="#58a6ff")
                                fig.tight_layout(); st.pyplot(fig); plt.close(fig)

                with t2:
                    c1,c2=st.columns(2)
                    tgt_c=c1.selectbox("Target (category)",df.columns.tolist(),key="c_t")
                    feats_c=c2.multiselect("Features",[c for c in num_cols if c!=tgt_c],key="c_f")
                    if st.button("▶ Run Classification",use_container_width=True,key="c_btn"):
                        with st.spinner("Training classifiers..."): res=ml.run_classification(tgt_c,feats_c or None)
                        if "error" in res: st.error(res["error"])
                        else:
                            st.markdown(f'<div class="ml-result"><div class="ml-best">🏆 {res["best_model"]} — {res["best_accuracy"]}% accuracy</div></div>', unsafe_allow_html=True)
                            fi=res.get("feature_importance",{})
                            if fi:
                                fi_s=pd.Series(fi).sort_values()
                                fig,ax=dfig(7,max(3,len(fi_s)*.4))
                                ax.barh(fi_s.index,fi_s.values,color="#bc8cff")
                                fig.tight_layout(); st.pyplot(fig); plt.close(fig)

                with t3:
                    c1,c2=st.columns(2)
                    n_c=c1.slider("Clusters (0=auto)",0,10,0)
                    feat_c=c2.multiselect("Features",num_cols,default=num_cols[:min(4,len(num_cols))],key="cl_f")
                    if st.button("▶ Find Clusters",use_container_width=True,key="cl_btn"):
                        with st.spinner("K-Means running..."): res=ml.run_clustering(n_c or None,feat_c or None)
                        if "error" in res: st.error(res["error"])
                        else:
                            st.success(f"✅ {res['n_clusters']} clusters | Silhouette={res['silhouette_score']} ({res['quality']})")
                            pcols=st.columns(min(res["n_clusters"],3))
                            for i,(name,prof) in enumerate(res.get("cluster_profiles",{}).items()):
                                with pcols[i%len(pcols)]:
                                    st.markdown(f"**{name}** — {prof['size']} records ({prof['pct']}%)")
                                    for cn,v in list(prof.get("means",{}).items())[:4]:
                                        st.markdown(f"<small style='color:#8b949e'>{cn}: <b style='color:#58a6ff'>{v}</b></small>",unsafe_allow_html=True)

                with t4:
                    c1,c2=st.columns(2)
                    tgt_f=c1.selectbox("Column to forecast",num_cols,key="f_t")
                    periods=c2.slider("Periods",3,24,6)
                    if st.button("▶ Forecast",use_container_width=True,key="f_btn"):
                        with st.spinner("Forecasting..."): res=ml.run_forecasting(tgt_f,periods)
                        if "error" in res: st.error(res["error"])
                        else:
                            st.success(f"{res['trend_direction']} | R²={res['r2_score']}")
                            hist=res.get("historical_values",[]); fc=res.get("forecast",[])
                            fig,ax=dfig(10,4)
                            ax.plot(range(len(hist)),hist,color="#58a6ff",linewidth=2,label="Historical")
                            ax.plot(range(len(hist),len(hist)+len(fc)),fc,color="#3fb950",linewidth=2.5,linestyle="--",label="Forecast",marker="o",markersize=5)
                            ax.axvline(x=len(hist)-1,color="#d29922",linestyle=":",alpha=.7)
                            ax.legend(framealpha=.3,labelcolor="#c9d1d9")
                            ax.set_title(f"Forecast: {tgt_f}",color="#e6edf3")
                            fig.tight_layout(); st.pyplot(fig); plt.close(fig)
                            fc_cols=st.columns(min(len(fc),6))
                            for i,(v,c) in enumerate(zip(fc,fc_cols)): c.metric(f"P{i+1}",v)
            except Exception as e:
                st.error(f"ML Error: {e}")

        # ── INSIGHTS ──────────────────────────────────
        elif page == "📢 Insights":
            st.markdown('<div class="card-title">📢 Step 5 — Communicate Insights</div>', unsafe_allow_html=True)
            t1,t2=st.tabs(["📋 Executive Summary","📖 Data Story"])

            ctx_str = f"""Dataset: {st.session_state.filename}, {sh.get('rows',0)} rows × {sh.get('columns',0)} cols
Goal: {st.session_state.goal_question or 'General analysis'}
Quality: {qr.get('quality_score',0)}/100
Stats: {json.dumps({c:{"mean":s.get("mean"),"std":s.get("std"),"outliers":s.get("outliers",{}).get("count",0)} for c,s in list(ns.items())[:6]})}
Correlations: {json.dumps(corr.get("strong_pairs",[])[:4])}"""

            with t1:
                if st.button("🚀 Generate Executive Summary",use_container_width=True,type="primary"):
                    prompt=f"""{ctx_str}
Generate executive summary. Return ONLY JSON:
{{"headline":"one powerful sentence with key finding + numbers","overview":"2-3 sentences","key_findings":[{{"finding":"specific with numbers","significance":"business impact","type":"positive/negative/neutral"}}],"data_story":"4-5 sentence narrative","anomalies":["unusual patterns"],"limitations":["data issues"]}}"""
                    with st.spinner("🤖 AI generating insights..."): result=ask_ai_json(prompt)
                    if "_raw" in result: st.markdown(result["_raw"])
                    else:
                        st.markdown(f"<h2 style='color:#58a6ff'>{result.get('headline','')}</h2>",unsafe_allow_html=True)
                        st.markdown(f"<p style='color:#c9d1d9;font-style:italic'>{result.get('overview','')}</p>",unsafe_allow_html=True)
                        st.markdown("---")
                        c1,c2=st.columns([1.2,1])
                        with c1:
                            st.markdown("**🔑 Key Findings:**")
                            type_colors={"positive":"#3fb950","negative":"#f85149","neutral":"#58a6ff"}
                            for f in result.get("key_findings",[]):
                                color=type_colors.get(f.get("type","neutral"),"#58a6ff")
                                st.markdown(f'<div class="insight-card"><div class="insight-title" style="color:{color}">{f.get("finding","")}</div><div class="insight-sub">{f.get("significance","")}</div></div>',unsafe_allow_html=True)
                        with c2:
                            st.markdown("**📖 Data Story:**")
                            st.markdown(f'<p style="color:#c9d1d9;line-height:1.7">{result.get("data_story","")}</p>',unsafe_allow_html=True)
                            for a in result.get("anomalies",[]):
                                st.markdown(f'<div class="insight-card insight-warn"><div class="insight-title">⚠️ {a}</div></div>',unsafe_allow_html=True)

            with t2:
                if st.button("🚀 Generate Data Story",use_container_width=True,type="primary"):
                    prompt=f"""{ctx_str}
Write a compelling data story. Return ONLY JSON:
{{"title":"compelling title","hook":"surprising opening insight","context":"background","plot":"main findings arc","climax":"most important discovery","resolution":"what to do","key_metrics":[{{"metric":"name","value":"number","context":"meaning"}}]}}"""
                    with st.spinner("🤖 Writing story..."): result=ask_ai_json(prompt)
                    if "_raw" in result: st.markdown(result["_raw"])
                    else:
                        st.markdown(f"<h2 style='color:#bc8cff'>{result.get('title','')}</h2>",unsafe_allow_html=True)
                        for section,label in [("hook","🎣 Hook"),("context","📚 Context"),("plot","📈 Plot"),("climax","⚡ Key Finding"),("resolution","🎯 Resolution")]:
                            if result.get(section):
                                st.markdown(f"**{label}:** {result[section]}")
                        km=result.get("key_metrics",[])
                        if km:
                            st.markdown("**📊 Key Metrics:**")
                            mcols=st.columns(min(len(km),4))
                            for i,(m,col) in enumerate(zip(km,mcols)): col.metric(m.get("metric",""),m.get("value",""),help=m.get("context",""))

        # ── ACTIONS ───────────────────────────────────
        elif page == "🎯 Actions":
            st.markdown('<div class="card-title">🎯 Step 6 — Recommend Actions</div>', unsafe_allow_html=True)
            ctx_str=f"""Dataset: {st.session_state.filename}
Goal: {st.session_state.goal_question or 'General analysis'}
{sh.get('rows',0)} rows | Quality: {qr.get('quality_score',0)}/100
Issues: {[i.get('message','') for i in qr.get('issues',[])[:3]]}
Stats: {json.dumps({c:{"mean":s.get("mean"),"outliers":s.get("outliers",{}).get("count",0)} for c,s in list(ns.items())[:5]})}"""

            if st.button("🚀 Generate Action Plan",use_container_width=True,type="primary"):
                prompt=f"""{ctx_str}
Generate prioritized action plan. Return ONLY JSON:
{{"immediate_actions":[{{"action":"specific NOW action","reason":"data evidence with numbers","impact":"high/medium/low","effort":"low/medium/high","timeline":"today/this week/this month","kpi":"how to measure"}}],"strategic_recommendations":[{{"recommendation":"strategic move","business_value":"quantified benefit","evidence":"data support"}}],"data_improvements":[{{"gap":"missing data","value":"what analysis it enables"}}],"watch_out":[{{"risk":"specific risk","indicator":"early warning sign","threshold":"alert level"}}]}}"""
                with st.spinner("🤖 Generating action plan..."): result=ask_ai_json(prompt)
                if "_raw" in result: st.markdown(result["_raw"])
                else:
                    st.markdown("### ⚡ Immediate Actions")
                    imp_e={"high":"🔴","medium":"🟡","low":"🟢"}
                    for i,action in enumerate(result.get("immediate_actions",[]),1):
                        imp=action.get("impact","medium").lower()
                        with st.expander(f"{imp_e.get(imp,'⚪')} {i}. {action.get('action','')}"):
                            c1,c2,c3=st.columns(3)
                            c1.metric("Impact",action.get("impact","—").title())
                            c2.metric("Effort",action.get("effort","—").title())
                            c3.metric("Timeline",action.get("timeline","—"))
                            st.info(f"📊 **Evidence:** {action.get('reason','')}")
                            st.caption(f"📏 Measure: {action.get('kpi','')}")

                    c1,c2=st.columns(2)
                    with c1:
                        recs=result.get("strategic_recommendations",[])
                        if recs:
                            st.markdown("### 🎯 Strategic Recommendations")
                            for rec in recs:
                                st.markdown(f'<div class="insight-card insight-pos"><div class="insight-title">{rec.get("recommendation","")}</div><div class="insight-sub">{rec.get("business_value","")}</div><div style="color:#58a6ff;font-size:11px;margin-top:4px">{rec.get("evidence","")}</div></div>',unsafe_allow_html=True)
                    with c2:
                        risks=result.get("watch_out",[])
                        if risks:
                            st.markdown("### 👀 Watch Out For")
                            for w in risks:
                                st.markdown(f'<div class="insight-card insight-warn"><div class="insight-title">{w.get("risk","")}</div><div class="insight-sub">Indicator: {w.get("indicator","")}</div><div style="color:#f85149;font-size:11px">Alert: {w.get("threshold","")}</div></div>',unsafe_allow_html=True)

                    improvements=result.get("data_improvements",[])
                    if improvements:
                        st.markdown("### 📈 Data Collection Gaps")
                        for imp in improvements:
                            st.markdown(f'<div class="insight-card"><div class="insight-title">{imp.get("gap","")}</div><div class="insight-sub">{imp.get("value","")}</div></div>',unsafe_allow_html=True)

        # ── PREVIEW ───────────────────────────────────
        elif page == "📋 Preview":
            st.markdown('<div class="card-title">📋 Data Preview</div>', unsafe_allow_html=True)
            c1,c2,c3=st.columns(3)
            c1.metric("Rows",f"{len(df):,}"); c2.metric("Columns",len(df.columns))
            c3.metric("Memory",f"{df.memory_usage(deep=True).sum()/1024:.1f} KB")
            n_rows=st.slider("Rows to show",10,min(500,len(df)),50)
            col_filter=st.multiselect("Filter columns",df.columns.tolist(),default=df.columns.tolist())
            if col_filter: st.dataframe(df[col_filter].head(n_rows),use_container_width=True,hide_index=True,height=400)
            st.markdown("**Column Info:**")
            info=[{"Column":c,"Type":str(df[c].dtype),"Non-Null":int(df[c].notna().sum()),"Null":int(df[c].isna().sum()),"Unique":int(df[c].nunique()),"Sample":str(df[c].dropna().iloc[0]) if len(df[c].dropna())>0 else "—"} for c in df.columns]
            st.dataframe(pd.DataFrame(info),use_container_width=True,hide_index=True)

        # ── EXPORT BUTTONS ────────────────────────────
        st.markdown("---")
        ec1,ec2,ec3=st.columns([1,1,4])
        csv_data=df.to_csv(index=False).encode()
        ec1.download_button("⬇ CSV",csv_data,f"{st.session_state.filename}.csv","text/csv",use_container_width=True)
        buf=io.BytesIO()
        with pd.ExcelWriter(buf,engine="xlsxwriter") as w: df.to_excel(w,index=False)
        ec2.download_button("📊 Excel",buf.getvalue(),f"{st.session_state.filename}.xlsx",use_container_width=True)