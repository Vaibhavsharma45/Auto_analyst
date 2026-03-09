"""
DataMind Pro v3 — Streamlit
Pro Dashboard — Full width + Fixed bottom chatbot
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

# ════════════════════════════════════════════════════════
# CSS — Pro Dashboard
# ════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp {
  background: #0d1117 !important;
  color: #e6edf3 !important;
  font-family: 'Syne', sans-serif !important;
}

/* Hide streamlit chrome */
#MainMenu, footer, [data-testid="stHeader"] { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="stToolbar"] { display: none !important; }

/* ── TOPBAR ── */
.topbar {
  position: fixed; top: 0; left: 0; right: 0; height: 56px; z-index: 1000;
  background: rgba(1,4,9,.95);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid #21262d;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 24px; gap: 16px;
}
.topbar-logo {
  font-size: 18px; font-weight: 800; color: #e6edf3;
  display: flex; align-items: center; gap: 8px; flex-shrink: 0;
}
.topbar-logo em { color: #58a6ff; font-style: normal; }
.topbar-logo sup { font-size: 9px; color: #bc8cff; vertical-align: super; }
.topbar-center { display: flex; gap: 2px; overflow-x: auto; flex: 1; justify-content: center; }
.topbar-center::-webkit-scrollbar { display: none; }
.topbar-right { display: flex; align-items: center; gap: 10px; flex-shrink: 0; }
.ds-chip {
  background: rgba(88,166,255,.1); border: 1px solid rgba(88,166,255,.25);
  color: #58a6ff; border-radius: 20px; padding: 3px 12px;
  font-size: 11px; font-weight: 600; white-space: nowrap;
}
.quality-chip {
  border-radius: 20px; padding: 3px 12px; font-size: 11px; font-weight: 700;
}
.q-green { background: rgba(63,185,80,.1); border: 1px solid rgba(63,185,80,.3); color: #3fb950; }
.q-orange { background: rgba(210,153,34,.1); border: 1px solid rgba(210,153,34,.3); color: #d29922; }
.q-red { background: rgba(248,81,73,.1); border: 1px solid rgba(248,81,73,.3); color: #f85149; }

/* ── NAV TABS ── */
.nav-btn {
  padding: 8px 14px; font-size: 12px; font-weight: 600;
  background: transparent; border: none; border-radius: 8px;
  color: #8b949e; cursor: pointer; font-family: 'Syne', sans-serif;
  white-space: nowrap; transition: all .2s;
}
.nav-btn:hover { background: rgba(88,166,255,.08); color: #e6edf3; }
.nav-btn.active { background: rgba(88,166,255,.12); color: #58a6ff; }

/* ── MAIN CONTENT AREA ── */
.main-wrap {
  margin-top: 56px;
  padding: 24px 28px 120px 28px;
  min-height: calc(100vh - 56px);
}

/* ── METRIC GRID ── */
.metric-row {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 12px; margin-bottom: 24px;
}
.metric-card {
  background: #161b22;
  border: 1px solid #21262d;
  border-radius: 12px; padding: 16px 14px;
  text-align: center;
  transition: border-color .2s;
}
.metric-card:hover { border-color: #388bfd; }
.metric-val {
  font-size: 24px; font-weight: 800;
  font-family: 'JetBrains Mono', monospace;
  line-height: 1.2; margin-bottom: 6px;
}
.metric-lbl { font-size: 10px; color: #8b949e; text-transform: uppercase; letter-spacing: .06em; }
.mv-blue { color: #58a6ff; }
.mv-purple { color: #bc8cff; }
.mv-green { color: #3fb950; }
.mv-orange { color: #d29922; }
.mv-red { color: #f85149; }

/* ── CARDS ── */
.card {
  background: #161b22; border: 1px solid #21262d;
  border-radius: 12px; padding: 20px; margin-bottom: 16px;
}
.card-hdr {
  font-size: 11px; font-weight: 700; color: #8b949e;
  text-transform: uppercase; letter-spacing: .07em;
  margin-bottom: 14px; display: flex; align-items: center; gap: 8px;
}
.card-hdr::after { content: ''; flex: 1; height: 1px; background: #21262d; }

/* ── FILL BARS ── */
.fill-row { margin: 7px 0; }
.fill-meta {
  display: flex; justify-content: space-between;
  font-size: 12px; margin-bottom: 4px; color: #c9d1d9;
}
.fill-bar { background: #21262d; border-radius: 4px; height: 5px; overflow: hidden; }
.fill-inner { height: 5px; border-radius: 4px; transition: width .4s; }

/* ── DATA TABLE ── */
.dt-wrap { overflow-x: auto; border-radius: 8px; border: 1px solid #21262d; }
table.dt { width: 100%; border-collapse: collapse; font-size: 12px; }
table.dt th {
  background: #0d1117; color: #58a6ff; padding: 10px 14px;
  text-align: left; font-size: 10px; text-transform: uppercase; letter-spacing: .06em;
  border-bottom: 1px solid #21262d; white-space: nowrap;
}
table.dt td {
  padding: 9px 14px; border-bottom: 1px solid rgba(33,38,45,.7);
  color: #c9d1d9; font-family: 'JetBrains Mono', monospace;
}
table.dt tr:hover td { background: rgba(88,166,255,.03); }
table.dt tr:last-child td { border-bottom: none; }

/* ── ISSUE BADGES ── */
.issue-badge {
  display: flex; align-items: center; gap: 10px;
  padding: 9px 14px; border-radius: 8px; margin: 5px 0; font-size: 12px;
}
.ib-critical { background: rgba(248,81,73,.07); border: 1px solid rgba(248,81,73,.2); color: #f85149; }
.ib-warning  { background: rgba(210,153,34,.07); border: 1px solid rgba(210,153,34,.2); color: #d29922; }
.ib-info     { background: rgba(88,166,255,.07); border: 1px solid rgba(88,166,255,.2); color: #58a6ff; }

/* ── INSIGHT CARDS ── */
.insight-item {
  border-left: 3px solid #58a6ff;
  background: #0d1117; padding: 12px 16px;
  border-radius: 0 10px 10px 0; margin: 8px 0;
}
.insight-item.pos { border-left-color: #3fb950; }
.insight-item.neg { border-left-color: #f85149; }
.insight-item.warn { border-left-color: #d29922; }
.ii-title { font-weight: 700; font-size: 13px; color: #e6edf3; margin-bottom: 3px; }
.ii-sub { font-size: 11px; color: #8b949e; }

/* ── ACTION CARDS ── */
.action-item {
  background: #161b22; border: 1px solid #21262d;
  border-radius: 10px; padding: 14px 16px; margin: 8px 0;
  display: grid; grid-template-columns: 32px 1fr auto; gap: 12px; align-items: start;
}
.action-num {
  width: 28px; height: 28px; border-radius: 50%;
  background: linear-gradient(135deg,#388bfd,#58a6ff);
  color: #fff; font-weight: 800; font-size: 12px;
  display: flex; align-items: center; justify-content: center;
}
.action-tags { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 6px; }
.tag {
  padding: 2px 10px; border-radius: 10px; font-size: 10px; font-weight: 700;
  text-transform: uppercase; letter-spacing: .04em;
}
.tag-high { background: rgba(248,81,73,.1); color: #f85149; }
.tag-med  { background: rgba(210,153,34,.1); color: #d29922; }
.tag-low  { background: rgba(63,185,80,.1);  color: #3fb950; }
.tag-blue { background: rgba(88,166,255,.1); color: #58a6ff; }
.tag-purple { background: rgba(188,140,255,.1); color: #bc8cff; }

/* ── FIXED CHATBOT ── */
#chatbot-fab {
  position: fixed; bottom: 24px; right: 24px; z-index: 2000;
}
.chat-fab-btn {
  width: 52px; height: 52px; border-radius: 50%;
  background: linear-gradient(135deg,#388bfd,#bc8cff);
  border: none; cursor: pointer; font-size: 22px;
  box-shadow: 0 4px 24px rgba(56,139,253,.4);
  display: flex; align-items: center; justify-content: center;
  transition: transform .2s; animation: pulse 2s infinite;
}
.chat-fab-btn:hover { transform: scale(1.1); }
@keyframes pulse {
  0%,100% { box-shadow: 0 4px 24px rgba(56,139,253,.4); }
  50% { box-shadow: 0 4px 32px rgba(188,140,255,.6); }
}
.chat-panel {
  position: fixed; bottom: 88px; right: 24px; z-index: 1999;
  width: 360px; height: 500px;
  background: #161b22; border: 1px solid #21262d;
  border-radius: 16px; display: flex; flex-direction: column;
  box-shadow: 0 20px 60px rgba(0,0,0,.5);
  overflow: hidden;
}
.chat-panel-hdr {
  padding: 14px 16px; background: #0d1117;
  border-bottom: 1px solid #21262d;
  display: flex; align-items: center; justify-content: space-between;
}
.chat-panel-title { display: flex; align-items: center; gap: 10px; }
.chat-av {
  width: 32px; height: 32px; border-radius: 50%;
  background: linear-gradient(135deg,#58a6ff,#bc8cff);
  display: flex; align-items: center; justify-content: center; font-size: 15px;
}
.chat-name { font-weight: 700; font-size: 13px; }
.chat-online { font-size: 10px; color: #3fb950; margin-top: 1px; }
.chat-close {
  background: transparent; border: none; color: #8b949e;
  cursor: pointer; font-size: 16px; padding: 4px 8px; border-radius: 6px;
}
.chat-close:hover { background: rgba(255,255,255,.05); color: #e6edf3; }
.chat-msgs-area {
  flex: 1; overflow-y: auto; padding: 12px;
  display: flex; flex-direction: column; gap: 8px;
  scroll-behavior: smooth;
}
.chat-msgs-area::-webkit-scrollbar { width: 4px; }
.chat-msgs-area::-webkit-scrollbar-track { background: transparent; }
.chat-msgs-area::-webkit-scrollbar-thumb { background: #21262d; border-radius: 2px; }
.chat-bubble {
  max-width: 88%; padding: 9px 12px; border-radius: 12px;
  font-size: 12px; line-height: 1.5;
}
.cb-user {
  background: rgba(56,139,253,.15); border: 1px solid rgba(88,166,255,.2);
  color: #e6edf3; align-self: flex-end; border-radius: 12px 12px 2px 12px;
}
.cb-ai {
  background: #0d1117; border: 1px solid #21262d;
  color: #c9d1d9; align-self: flex-start; border-radius: 12px 12px 12px 2px;
}
.chat-quick-pills {
  display: flex; gap: 5px; padding: 8px 12px; flex-wrap: wrap;
  border-top: 1px solid #21262d;
}
.qpill {
  padding: 4px 10px; background: rgba(88,166,255,.06);
  border: 1px solid rgba(88,166,255,.15); border-radius: 12px;
  font-size: 10px; color: #58a6ff; cursor: pointer; font-weight: 600;
  font-family: 'Syne', sans-serif; transition: all .2s; white-space: nowrap;
}
.qpill:hover { background: rgba(88,166,255,.15); }
.chat-input-area {
  padding: 10px 12px; border-top: 1px solid #21262d;
  display: flex; gap: 8px; align-items: center;
}

/* ── GOAL GRID ── */
.goal-grid {
  display: grid; grid-template-columns: repeat(3,1fr); gap: 12px; margin: 16px 0;
}
.goal-card {
  background: #161b22; border: 2px solid #21262d; border-radius: 12px;
  padding: 18px 14px; text-align: center; cursor: pointer; transition: all .2s;
}
.goal-card:hover { border-color: #388bfd; transform: translateY(-1px); }
.goal-card.sel { border-color: #58a6ff; background: rgba(88,166,255,.06); }
.gc-icon { font-size: 28px; margin-bottom: 8px; }
.gc-title { font-weight: 700; font-size: 13px; margin-bottom: 4px; }
.gc-sub { font-size: 11px; color: #8b949e; }

/* ── UPLOAD ── */
.upload-hero {
  text-align: center; padding: 48px 24px;
  border: 2px dashed #21262d; border-radius: 16px;
  background: rgba(88,166,255,.02); transition: all .3s; cursor: pointer;
}
.upload-hero:hover { border-color: #58a6ff; background: rgba(88,166,255,.05); }
.upload-icon { font-size: 52px; margin-bottom: 12px; }
.upload-title { font-size: 20px; font-weight: 700; margin-bottom: 6px; }
.upload-sub { color: #8b949e; font-size: 13px; }

/* ── STREAMLIT OVERRIDES ── */
.stButton > button {
  background: linear-gradient(135deg,#388bfd,#58a6ff) !important;
  color: #fff !important; border: none !important;
  border-radius: 8px !important; font-weight: 700 !important;
  font-family: 'Syne', sans-serif !important;
  transition: all .2s !important;
}
.stButton > button:hover { opacity: .9 !important; transform: translateY(-1px) !important; }
.stDownloadButton > button {
  background: transparent !important; color: #58a6ff !important;
  border: 1px solid #21262d !important; border-radius: 8px !important;
  font-weight: 600 !important; font-family: 'Syne', sans-serif !important;
}
.stDownloadButton > button:hover { border-color: #58a6ff !important; }
.stTextInput > div > div > input {
  background: #161b22 !important; border: 1px solid #21262d !important;
  color: #e6edf3 !important; border-radius: 8px !important;
  font-family: 'Syne', sans-serif !important;
}
.stTextInput > div > div > input:focus { border-color: #388bfd !important; }
.stSelectbox > div > div {
  background: #161b22 !important; border: 1px solid #21262d !important;
  border-radius: 8px !important; color: #e6edf3 !important;
}
.stMultiSelect > div {
  background: #161b22 !important; border: 1px solid #21262d !important;
  border-radius: 8px !important;
}
div[data-testid="stDataFrame"] {
  border: 1px solid #21262d !important; border-radius: 10px !important; overflow: hidden;
}
.stTabs [data-baseweb="tab-list"] { background: transparent; border-bottom: 1px solid #21262d; gap: 4px; }
.stTabs [data-baseweb="tab"] {
  background: transparent !important; color: #8b949e !important;
  border-radius: 8px 8px 0 0 !important; font-weight: 600 !important;
  font-family: 'Syne', sans-serif !important;
}
.stTabs [aria-selected="true"] { color: #58a6ff !important; background: rgba(88,166,255,.06) !important; }
div[data-testid="stChatInput"] > div {
  background: #0d1117 !important; border: 1px solid #21262d !important;
  border-radius: 10px !important;
}
.stAlert { border-radius: 10px !important; font-family: 'Syne', sans-serif !important; }
.stSlider > div > div > div > div { background: #58a6ff !important; }
.stMarkdown h1,.stMarkdown h2,.stMarkdown h3 { color: #e6edf3 !important; font-family: 'Syne', sans-serif !important; }

@media (max-width: 768px) {
  .metric-row { grid-template-columns: repeat(3,1fr) !important; }
  .goal-grid { grid-template-columns: repeat(2,1fr) !important; }
  .topbar-center { display: none; }
  .chat-panel { width: calc(100vw - 32px); right: 16px; }
}
</style>
""", unsafe_allow_html=True)

PALETTE = ["#58a6ff","#bc8cff","#3fb950","#d29922","#f85149","#79c0ff","#ffa657","#ff7b72"]

# ── STATE ────────────────────────────────────────────
for k,v in {"df":None,"filename":None,"analysis":None,"goal_type":"custom",
             "goal_question":"","chat_history":[],"page":"📊 Overview",
             "chat_open":False,"ml_cache":{}}.items():
    if k not in st.session_state: st.session_state[k]=v

# ── AI ───────────────────────────────────────────────
def ask_ai(prompt, system="You are DataMind AI — expert data analyst. Reply in Hinglish. Use specific numbers. Use markdown.", history=None):
    import requests
    key = os.getenv("GROQ_API_KEY","") or (st.secrets.get("GROQ_API_KEY","") if hasattr(st,"secrets") else "")
    if not key: return "⚠️ GROQ_API_KEY not set. Add in Streamlit Cloud → App Settings → Secrets."
    msgs = [{"role":"system","content":system}]
    if history: msgs += [m for m in history[-8:] if m.get("role") in ("user","assistant")]
    msgs.append({"role":"user","content":prompt})
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},
            json={"model":"llama-3.3-70b-versatile","messages":msgs,"max_tokens":2000,"temperature":0.7},timeout=45)
        return r.json()["choices"][0]["message"]["content"] if r.status_code==200 else f"❌ API {r.status_code}: {r.text[:100]}"
    except Exception as e: return f"❌ {e}"

def ask_ai_json(prompt):
    r = ask_ai(prompt,"You are a data analyst. Return ONLY valid JSON — no markdown, no backticks, no preamble.")
    try: return json.loads(r.replace("```json","").replace("```","").strip())
    except: return {"_raw":r}

# ── DATA ─────────────────────────────────────────────
def load_file(f):
    n=f.name.lower()
    if n.endswith(".csv"): return pd.read_csv(f)
    if n.endswith(".tsv"): return pd.read_csv(f,sep="\t")
    if n.endswith((".xlsx",".xls")): return pd.read_excel(f)
    if n.endswith(".json"): return pd.read_json(f)
    raise ValueError(f"Unsupported: {n}")

@st.cache_data(show_spinner=False)
def run_eda(key,_df):
    try:
        from backend.analysis.eda_engine import EDAEngine
        return EDAEngine(_df).run_full_analysis()
    except: return _basic_eda(_df)

def _basic_eda(df):
    nc=df.select_dtypes(include=np.number).columns.tolist()
    cc=df.select_dtypes(include="object").columns.tolist()
    ns={}
    for c in nc:
        s=df[c].dropna()
        if not len(s): continue
        q1,q3=s.quantile(.25),s.quantile(.75); iqr=q3-q1
        ns[c]={"mean":round(float(s.mean()),2),"median":round(float(s.median()),2),
               "std":round(float(s.std()),2),"min":round(float(s.min()),2),"max":round(float(s.max()),2),
               "outliers":{"count":int(((s<q1-1.5*iqr)|(s>q3+1.5*iqr)).sum())},"skewness":round(float(s.skew()),3)}
    cs={}
    for c in cc[:5]:
        vc=df[c].value_counts().head(6)
        cs[c]={"unique_values":int(df[c].nunique()),"value_counts":vc.to_dict()}
    pairs=[]
    if len(nc)>=2:
        cm=df[nc].corr()
        for i in range(len(nc)):
            for j in range(i+1,len(nc)):
                r=float(cm.iloc[i,j])
                if abs(r)>=.5: pairs.append({"col1":nc[i],"col2":nc[j],"pearson_r":round(r,3),"strength":"strong" if abs(r)>=.7 else "moderate"})
        pairs.sort(key=lambda x:abs(x["pearson_r"]),reverse=True)
    miss=int(df.isnull().sum().sum()); dups=int(df.duplicated().sum())
    score=100; issues=[]
    if miss>0: pct=miss/(df.shape[0]*df.shape[1])*100; score-=min(30,int(pct*3)); issues.append({"severity":"warning","message":f"{miss} missing values ({pct:.1f}%)"})
    if dups>0: score-=min(20,dups); issues.append({"severity":"warning","message":f"{dups} duplicate rows"})
    for c,s in ns.items():
        if s["outliers"]["count"]>len(df)*.05: issues.append({"severity":"info","message":f"{c}: {s['outliers']['count']} outliers"})
    return {"overview":{"shape":{"rows":len(df),"columns":len(df.columns)},
            "missing":{"total_missing_cells":miss},"duplicates":{"duplicate_rows":dups},
            "column_types":{"numeric":nc,"categorical":cc}},
            "numeric_stats":ns,"categorical_stats":cs,
            "correlations":{"strong_pairs":pairs[:8]},
            "quality_report":{"quality_score":max(0,score),"issues":issues,"recommendations":[],"total_issues":len(issues)}}

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
# SHORTCUTS
# ════════════════════════════════════════════════════════
df = st.session_state.df
a  = st.session_state.analysis or {}
ov = a.get("overview",{}); sh=ov.get("shape",{})
ns = a.get("numeric_stats",{}); cs=a.get("categorical_stats",{})
qr = a.get("quality_report",{}); corr=a.get("correlations",{})
num_cols = df.select_dtypes(include=np.number).columns.tolist() if df is not None else []
cat_cols = df.select_dtypes(include="object").columns.tolist() if df is not None else []
score = qr.get("quality_score",0)
q_cls = "q-green" if score>=80 else ("q-orange" if score>=60 else "q-red")

# ════════════════════════════════════════════════════════
# TOPBAR
# ════════════════════════════════════════════════════════
pages = ["📊 Overview","🧹 Clean","📈 Charts","🤖 ML","📢 Insights","🎯 Actions","📋 Preview"]
ds_html = f'<span class="ds-chip">📁 {st.session_state.filename} &nbsp;·&nbsp; {sh.get("rows",0):,}×{sh.get("columns",0)}</span><span class="quality-chip {q_cls}">Q: {score}/100</span>' if df is not None else '<span style="color:#8b949e;font-size:12px">Upload a dataset to start</span>'

# Build nav buttons HTML
nav_html = ""
for pg in pages:
    active = "active" if st.session_state.page == pg else ""
    nav_html += f'<span class="nav-btn {active}">{pg}</span>'

st.markdown(f"""
<div class="topbar">
  <div class="topbar-logo">⚡ Data<em>Mind</em> Pro <sup>v3</sup></div>
  <div class="topbar-center">{nav_html}</div>
  <div class="topbar-right">{ds_html}</div>
</div>
""", unsafe_allow_html=True)

# Real nav buttons (hidden visually but functional)
# We use a pill row below topbar for actual navigation
if df is not None:
    nav_cols = st.columns(len(pages)+1)
    for i,(pg,col) in enumerate(zip(pages,nav_cols)):
        if col.button(pg, key=f"nb_{i}", use_container_width=True):
            st.session_state.page = pg; st.rerun()
    if nav_cols[-1].button("↺", key="nb_reset", use_container_width=True):
        for k in ["df","filename","analysis","chat_history","ml_cache"]:
            st.session_state[k] = None if k not in ["chat_history","ml_cache"] else ([] if k=="chat_history" else {})
        st.session_state.page = "📊 Overview"; st.rerun()

    # Style the nav buttons to look like topbar
    st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"]:first-of-type .stButton>button {
        background: transparent !important; color: #8b949e !important;
        border: none !important; border-radius: 8px !important;
        font-size: 12px !important; padding: 6px 10px !important;
        box-shadow: none !important;
    }
    div[data-testid="stHorizontalBlock"]:first-of-type .stButton>button:hover {
        background: rgba(88,166,255,.08) !important; color: #e6edf3 !important;
        transform: none !important;
    }
    </style>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# HOME — UPLOAD
# ════════════════════════════════════════════════════════
if df is None:
    st.markdown('<div class="main-wrap">', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns([1.4, 1], gap="large")

    with c1:
        st.markdown("""
        <h1 style='font-size:46px;font-weight:800;line-height:1.15;margin-bottom:8px'>
          Ask the <span style='color:#58a6ff'>Right</span><br>Question
        </h1>
        <p style='color:#8b949e;font-size:15px;margin-bottom:28px'>
          Insight without a clear question = wasted effort.
        </p>""", unsafe_allow_html=True)

        # Feature chips
        feats = ["📊 EDA","🤖 ML Models","💬 AI Chat","📈 Charts","📢 Insights","🎯 Actions"]
        fc = st.columns(3)
        for i,f in enumerate(feats):
            fc[i%3].markdown(f'<div style="background:#161b22;border:1px solid #21262d;border-radius:20px;padding:6px 12px;text-align:center;font-size:12px;color:#58a6ff;margin-bottom:8px">{f}</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**🎯 Your analysis goal:**")
        goals = [("🛒","Sales","Revenue & targets"),("👥","Customer","Segments & churn"),
                 ("🏢","HR","Salary & attrition"),("💰","Financial","Profit & ROI"),
                 ("⚙️","Operations","Supply chain"),("🔬","Custom","Define your own")]
        gc = st.columns(3)
        for i,(icon,title,sub) in enumerate(goals):
            with gc[i%3]:
                sel = st.session_state.goal_type == title
                if st.button(f"{icon} {title}", key=f"g_{i}", use_container_width=True):
                    st.session_state.goal_type = title; st.rerun()
                st.markdown(f'<div style="font-size:10px;color:#8b949e;text-align:center;margin:-6px 0 8px">{sub}</div>', unsafe_allow_html=True)

        q = st.text_input("", placeholder="e.g. Which products are underperforming this quarter?", label_visibility="collapsed", key="gq")
        if q: st.session_state.goal_question = q

    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("### 📂 Upload Dataset")
        uploaded = st.file_uploader("CSV · Excel · JSON · TSV — max 100MB", type=["csv","xlsx","xls","json","tsv"], label_visibility="collapsed")

        st.markdown("**Or try a sample:**")
        s1,s2,s3 = st.columns(3)
        SAMPLES = {
            "sales":("sales.csv","month,product,category,sales,units,profit,region,target\nJan,Laptop,Electronics,145000,29,42000,North,130000\nJan,Phone,Electronics,89000,89,22000,South,80000\nFeb,Laptop,Electronics,167000,33,48000,North,150000\nFeb,Shoes,Apparel,41000,136,11000,South,38000\nMar,TV,Electronics,78000,15,18000,North,75000\nApr,Phone,Electronics,103000,103,26000,North,95000\nApr,Laptop,Electronics,188000,37,55000,South,170000\nMay,Laptop,Electronics,172000,34,50000,West,160000\nJun,TV,Electronics,101000,19,23000,North,95000\nJun,Laptop,Electronics,195000,39,57000,West,180000"),
            "hr":("hr.csv","id,name,department,age,salary,experience,rating,city,gender,promoted\nE001,Rahul,Engineering,28,75000,4,4.2,Delhi,M,No\nE002,Priya,Marketing,32,65000,7,4.5,Mumbai,F,Yes\nE003,Amit,Engineering,35,92000,10,4.8,Bangalore,M,Yes\nE004,Sneha,HR,27,48000,3,3.9,Delhi,F,No\nE005,Vikram,Engineering,30,82000,6,4.3,Hyderabad,M,No\nE006,Rajesh,Finance,40,110000,15,4.6,Mumbai,M,Yes\nE007,Kavita,Engineering,26,68000,2,3.8,Bangalore,F,No\nE008,Deepa,Finance,37,98000,12,4.7,Hyderabad,F,Yes"),
            "ecomm":("ecomm.csv","order_id,product,category,price,qty,discount,rating,delivery_days,returned\nORD001,Earbuds,Electronics,2499,1,10,4.3,3,No\nORD002,Kurta,Clothing,899,2,5,4.1,5,No\nORD003,Python Book,Books,599,1,0,4.7,4,No\nORD004,Shoes,Footwear,3499,1,15,3.9,6,Yes\nORD005,Speaker,Electronics,1999,1,8,4.5,3,No\nORD006,Watch,Electronics,8999,1,12,4.6,3,Yes\nORD007,Yoga Mat,Sports,1499,1,0,4.4,5,No\nORD008,Jeans,Clothing,1299,1,10,4.0,5,No"),
        }
        load_s = None
        with s1:
            if st.button("🛒 Sales", use_container_width=True): load_s="sales"
        with s2:
            if st.button("👥 HR", use_container_width=True): load_s="hr"
        with s3:
            if st.button("📦 E-comm", use_container_width=True): load_s="ecomm"

        def load_and_run(dataframe, fname):
            st.session_state.df = dataframe; st.session_state.filename = fname
            with st.spinner("⚡ Analyzing..."): st.session_state.analysis = run_eda(fname+str(dataframe.shape), dataframe)

        if load_s:
            fname,csv = SAMPLES[load_s]; load_and_run(pd.read_csv(io.StringIO(csv)), fname); st.rerun()
        if uploaded:
            try: load_and_run(load_file(uploaded), uploaded.name); st.rerun()
            except Exception as e: st.error(f"❌ {e}")

    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# ANALYSIS PAGES
# ════════════════════════════════════════════════════════
else:
    page = st.session_state.page
    st.markdown('<div class="main-wrap">', unsafe_allow_html=True)

    # ── OVERVIEW ─────────────────────────────────────
    if page == "📊 Overview":
        miss = ov.get('missing',{}).get('total_missing_cells',0)
        dups = ov.get('duplicates',{}).get('duplicate_rows',0)
        mv = "mv-orange" if miss>0 else "mv-green"
        dv = "mv-orange" if dups>0 else "mv-green"
        st.markdown(f"""
        <div class="metric-row">
          <div class="metric-card"><div class="metric-val mv-blue">{sh.get('rows',0):,}</div><div class="metric-lbl">Total Rows</div></div>
          <div class="metric-card"><div class="metric-val mv-purple">{sh.get('columns',0)}</div><div class="metric-lbl">Columns</div></div>
          <div class="metric-card"><div class="metric-val {mv}">{miss}</div><div class="metric-lbl">Missing Values</div></div>
          <div class="metric-card"><div class="metric-val {dv}">{dups}</div><div class="metric-lbl">Duplicates</div></div>
          <div class="metric-card"><div class="metric-val mv-blue">{len(num_cols)}</div><div class="metric-lbl">Numeric Cols</div></div>
          <div class="metric-card"><div class="metric-val {'mv-green' if score>=80 else 'mv-orange' if score>=60 else 'mv-red'}">{score}</div><div class="metric-lbl">Quality /100</div></div>
        </div>""", unsafe_allow_html=True)

        col1, col2 = st.columns([1.6, 1], gap="large")
        with col1:
            st.markdown('<div class="card"><div class="card-hdr">📈 Statistical Summary</div>', unsafe_allow_html=True)
            if ns:
                rows = [{"Column":c,"Mean":s.get("mean"),"Median":s.get("median"),"Std":s.get("std"),"Min":s.get("min"),"Max":s.get("max"),"Outliers":s.get("outliers",{}).get("count",0)} for c,s in ns.items()]
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=min(380,len(rows)*38+40))
            st.markdown('</div>', unsafe_allow_html=True)

            if cs:
                st.markdown('<div class="card"><div class="card-hdr">🏷️ Categorical Columns</div>', unsafe_allow_html=True)
                cat_show = list(cs.keys())[:4]
                ccols = st.columns(min(len(cat_show),4))
                for i,(cn,cd) in enumerate([(c,cs[c]) for c in cat_show]):
                    with ccols[i]:
                        vc=cd.get("value_counts",{})
                        if vc:
                            fig,ax=dfig(3.5,2.8)
                            items=list(vc.items())[:5]
                            ax.bar([str(x[0])[:10] for x in items],[x[1] for x in items],color=PALETTE[i%len(PALETTE)],alpha=.85)
                            ax.set_title(cn,fontsize=10,color="#e6edf3")
                            plt.xticks(rotation=25,ha="right",fontsize=7)
                            fig.tight_layout(); st.pyplot(fig); plt.close(fig)
                st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            strong=corr.get("strong_pairs",[])
            if strong:
                st.markdown('<div class="card"><div class="card-hdr">🔗 Top Correlations</div>', unsafe_allow_html=True)
                for p in strong[:6]:
                    r=p.get("pearson_r",0); pct=int(abs(r)*100)
                    col=("#3fb950" if r>0 else "#f85149")
                    st.markdown(f"""<div class="fill-row"><div class="fill-meta"><span>{p['col1'][:12]} ↔ {p['col2'][:12]}</span><span style="color:{col};font-weight:700">{r}</span></div><div class="fill-bar"><div class="fill-inner" style="width:{pct}%;background:{col}"></div></div></div>""", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            issues=qr.get("issues",[])
            if issues:
                st.markdown('<div class="card"><div class="card-hdr">⚠️ Data Quality</div>', unsafe_allow_html=True)
                for issue in issues[:6]:
                    sev=issue.get("severity","info")
                    icon={"critical":"🔴","warning":"⚠️","info":"ℹ️"}.get(sev,"ℹ️")
                    st.markdown(f'<div class="issue-badge ib-{sev}">{icon} {issue["message"]}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # Export
            st.markdown('<div class="card"><div class="card-hdr">📥 Export</div>', unsafe_allow_html=True)
            csv_d=df.to_csv(index=False).encode()
            st.download_button("⬇ Download CSV", csv_d, f"{st.session_state.filename}.csv","text/csv",use_container_width=True)
            buf=io.BytesIO()
            with pd.ExcelWriter(buf,engine="xlsxwriter") as w: df.to_excel(w,index=False)
            st.download_button("📊 Download Excel", buf.getvalue(), f"{st.session_state.filename}.xlsx",use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # ── CLEAN ─────────────────────────────────────────
    elif page == "🧹 Clean":
        st.markdown('<div class="card"><div class="card-hdr">🧹 Step 3 — Clean & Transform</div>', unsafe_allow_html=True)
        c1,c2=st.columns([1,1.8],gap="large")
        with c1:
            op=st.selectbox("Operation",["drop_duplicates","drop_column","fill_mean","fill_median","fill_zero","fill_unknown","normalize","rename_column","filter_rows","sort_asc","sort_desc","drop_na_rows"])
            col_sel=st.selectbox("Column",["—"]+df.columns.tolist())
            extra=""
            if op=="rename_column": extra=st.text_input("New name")
            if op=="filter_rows": extra=st.text_input("Contains value")
            if st.button("▶ Apply Operation", use_container_width=True):
                try:
                    ndf=df.copy(); msg=""
                    if op=="drop_duplicates": b=len(ndf); ndf=ndf.drop_duplicates(); msg=f"Removed {b-len(ndf)} duplicates"
                    elif op=="drop_column" and col_sel!="—": ndf=ndf.drop(columns=[col_sel]); msg=f"Dropped {col_sel}"
                    elif op=="fill_mean" and col_sel!="—": ndf[col_sel]=ndf[col_sel].fillna(ndf[col_sel].mean()); msg=f"Filled {col_sel} with mean"
                    elif op=="fill_median" and col_sel!="—": ndf[col_sel]=ndf[col_sel].fillna(ndf[col_sel].median()); msg=f"Filled {col_sel} with median"
                    elif op=="fill_zero" and col_sel!="—": ndf[col_sel]=ndf[col_sel].fillna(0); msg=f"Filled {col_sel} with 0"
                    elif op=="fill_unknown" and col_sel!="—": ndf[col_sel]=ndf[col_sel].fillna("Unknown"); msg=f"Filled {col_sel}"
                    elif op=="normalize" and col_sel!="—":
                        mn,mx=ndf[col_sel].min(),ndf[col_sel].max(); ndf[col_sel]=(ndf[col_sel]-mn)/(mx-mn+1e-9); msg=f"Normalized {col_sel}"
                    elif op=="rename_column" and col_sel!="—" and extra: ndf=ndf.rename(columns={col_sel:extra}); msg=f"Renamed → {extra}"
                    elif op=="filter_rows" and col_sel!="—" and extra:
                        b=len(ndf); ndf=ndf[ndf[col_sel].astype(str).str.contains(extra,na=False)]; msg=f"Filtered: {len(ndf)}/{b} rows"
                    elif op=="sort_asc" and col_sel!="—": ndf=ndf.sort_values(col_sel); msg=f"Sorted ↑ by {col_sel}"
                    elif op=="sort_desc" and col_sel!="—": ndf=ndf.sort_values(col_sel,ascending=False); msg=f"Sorted ↓ by {col_sel}"
                    elif op=="drop_na_rows": b=len(ndf); ndf=ndf.dropna(); msg=f"Dropped {b-len(ndf)} rows"
                    if msg:
                        st.session_state.df=ndf
                        with st.spinner("Re-analyzing..."): st.session_state.analysis=run_eda(op+str(ndf.shape),ndf)
                        st.success(f"✅ {msg}"); st.rerun()
                    else: st.warning("Select a valid column")
                except Exception as e: st.error(f"❌ {e}")
        with c2:
            st.caption(f"`{len(df):,} rows × {len(df.columns)} cols`")
            st.dataframe(df.head(40),use_container_width=True,hide_index=True,height=450)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── CHARTS ────────────────────────────────────────
    elif page == "📈 Charts":
        t1,t2,t3,t4,t5=st.tabs(["📊 Distributions","🔗 Heatmap","📦 Box Plots","🔵 Scatter","🛠 Custom"])
        with t1:
            if num_cols:
                sel=st.multiselect("Select columns",num_cols,default=num_cols[:min(4,len(num_cols))],key="d_s")
                if sel:
                    n=len(sel); fig,axes=plt.subplots(1,n,figsize=(5*n,4)); fig.patch.set_facecolor("#0d1117")
                    if n==1: axes=[axes]
                    for i,c in enumerate(sel):
                        axes[i].set_facecolor("#161b22"); axes[i].hist(df[c].dropna(),bins=25,color=PALETTE[i%len(PALETTE)],alpha=.85,edgecolor="none")
                        axes[i].set_title(c,color="#e6edf3",fontsize=11); axes[i].tick_params(colors="#8b949e")
                        for sp in axes[i].spines.values(): sp.set_edgecolor("#21262d")
                    fig.tight_layout(); st.pyplot(fig); plt.close(fig)
        with t2:
            if len(num_cols)>=2:
                sel2=st.multiselect("Columns",num_cols,default=num_cols[:min(8,len(num_cols))],key="hm_s")
                if len(sel2)>=2:
                    cm=df[sel2].corr(); fig,ax=plt.subplots(figsize=(max(6,len(sel2)*1.2),max(5,len(sel2))))
                    fig.patch.set_facecolor("#0d1117"); ax.set_facecolor("#161b22")
                    sns.heatmap(cm,annot=True,fmt=".2f",cmap="coolwarm",center=0,ax=ax,linewidths=.5,linecolor="#21262d",cbar_kws={"shrink":.8})
                    ax.tick_params(colors="#c9d1d9",labelsize=9); ax.set_title("Correlation Heatmap",color="#e6edf3")
                    fig.tight_layout(); st.pyplot(fig); plt.close(fig)
        with t3:
            if num_cols:
                sel3=st.multiselect("Columns",num_cols,default=num_cols[:min(4,len(num_cols))],key="bp_s")
                if sel3:
                    n=len(sel3); fig,axes=plt.subplots(1,n,figsize=(4*n,5)); fig.patch.set_facecolor("#0d1117")
                    if n==1: axes=[axes]
                    for i,c in enumerate(sel3):
                        axes[i].set_facecolor("#161b22")
                        bp=axes[i].boxplot([df[c].dropna()],patch_artist=True,
                            medianprops={"color":"#3fb950","linewidth":2.5},whiskerprops={"color":"#8b949e"},
                            capprops={"color":"#8b949e"},flierprops={"marker":"o","markersize":3,"alpha":.4})
                        bp["boxes"][0].set(facecolor="#58a6ff22",edgecolor="#58a6ff")
                        axes[i].set_title(c,color="#e6edf3"); axes[i].set_xticks([])
                        axes[i].tick_params(colors="#8b949e")
                        for sp in axes[i].spines.values(): sp.set_edgecolor("#21262d")
                    fig.tight_layout(); st.pyplot(fig); plt.close(fig)
        with t4:
            if len(num_cols)>=2:
                c1,c2,c3=st.columns(3)
                xc=c1.selectbox("X",num_cols,key="sx"); yc=c2.selectbox("Y",num_cols,index=min(1,len(num_cols)-1),key="sy")
                hue=c3.selectbox("Color by",["None"]+cat_cols,key="sh")
                fig,ax=dfig(10,5)
                if hue!="None":
                    for i,cat in enumerate(df[hue].unique()[:8]):
                        m=df[hue]==cat; ax.scatter(df[m][xc],df[m][yc],label=str(cat),color=PALETTE[i%len(PALETTE)],alpha=.6,s=40)
                    ax.legend(framealpha=.3,labelcolor="#c9d1d9")
                else: ax.scatter(df[xc],df[yc],color="#58a6ff",alpha=.5,s=30)
                ax.set_xlabel(xc); ax.set_ylabel(yc); ax.set_title(f"{xc} vs {yc}",color="#e6edf3")
                fig.tight_layout(); st.pyplot(fig); plt.close(fig)
        with t5:
            c1,c2,c3=st.columns(3)
            ct=c1.selectbox("Type",["bar","line","pie","histogram","area"],key="ct")
            xc=c2.selectbox("X",df.columns.tolist(),key="cx"); yc=c3.selectbox("Y",["count"]+num_cols,key="cy")
            if st.button("⚡ Generate",use_container_width=True):
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
                        [tx.set_color("#c9d1d9") for tx in t]; [tx.set_color("#0d1117") for tx in at]
                    elif ct=="histogram":
                        ch=yc if yc!="count" else xc; ax.hist(df[ch].dropna(),bins=30,color="#58a6ff",alpha=.85,edgecolor="none"); ax.set_xlabel(ch)
                    elif ct=="area":
                        yd=df[yc] if yc!="count" else df[xc].value_counts().sort_index()
                        ax.fill_between(range(len(yd)),yd.values,alpha=.4,color="#58a6ff")
                        ax.plot(range(len(yd)),yd.values,color="#58a6ff",linewidth=2)
                    ax.set_title(f"{ct.title()} — {xc}",color="#e6edf3",fontsize=13)
                    fig.tight_layout(); st.pyplot(fig); plt.close(fig)
                except Exception as e: st.error(f"Chart error: {e}")

    # ── ML ────────────────────────────────────────────
    elif page == "🤖 ML":
        st.markdown('<div class="card-hdr">🤖 ML Predictions — Regression · Classification · Clustering · Forecasting</div>', unsafe_allow_html=True)
        try:
            from backend.analysis.ml_engine import MLEngine; ml=MLEngine(df)
            t1,t2,t3,t4=st.tabs(["📈 Regression","🏷 Classification","🔵 Clustering","🔮 Forecasting"])
            with t1:
                c1,c2=st.columns(2)
                tgt=c1.selectbox("Target",num_cols,key="rt"); feats=c2.multiselect("Features (empty=auto)",[c for c in num_cols if c!=tgt],key="rf")
                if st.button("▶ Run Regression",use_container_width=True,key="rb"):
                    with st.spinner("Training 4 models..."): res=ml.run_regression(tgt,feats or None)
                    if "error" in res: st.error(res["error"])
                    else:
                        st.success(f"🏆 **{res['best_model']}** — R² = `{res['best_r2']}`")
                        st.caption(res.get("interpretation",""))
                        mr=res.get("model_results",{})
                        rows=[{"Model":m,"R²":v.get("r2","—"),"RMSE":v.get("rmse","—"),"MAE":v.get("mae","—")} for m,v in mr.items() if "error" not in v]
                        if rows: st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
                        fi=res.get("feature_importance",{})
                        if fi:
                            fi_s=pd.Series(fi).sort_values(); fig,ax=dfig(8,max(3,len(fi_s)*.5))
                            ax.barh(fi_s.index,fi_s.values,color="#58a6ff"); fig.tight_layout(); st.pyplot(fig); plt.close(fig)
            with t2:
                c1,c2=st.columns(2)
                tgt_c=c1.selectbox("Target",df.columns.tolist(),key="ct"); feats_c=c2.multiselect("Features",[c for c in num_cols if c!=tgt_c],key="cf")
                if st.button("▶ Run Classification",use_container_width=True,key="cb"):
                    with st.spinner("Training..."): res=ml.run_classification(tgt_c,feats_c or None)
                    if "error" in res: st.error(res["error"])
                    else:
                        st.success(f"🏆 **{res['best_model']}** — {res['best_accuracy']}% accuracy")
                        fi=res.get("feature_importance",{})
                        if fi:
                            fi_s=pd.Series(fi).sort_values(); fig,ax=dfig(8,max(3,len(fi_s)*.5))
                            ax.barh(fi_s.index,fi_s.values,color="#bc8cff"); fig.tight_layout(); st.pyplot(fig); plt.close(fig)
            with t3:
                c1,c2=st.columns(2)
                n_c=c1.slider("Clusters (0=auto)",0,10,0); feat_c=c2.multiselect("Features",num_cols,default=num_cols[:min(4,len(num_cols))],key="clf")
                if st.button("▶ Find Clusters",use_container_width=True,key="clb"):
                    with st.spinner("K-Means..."): res=ml.run_clustering(n_c or None,feat_c or None)
                    if "error" in res: st.error(res["error"])
                    else:
                        st.success(f"✅ {res['n_clusters']} clusters | Silhouette={res['silhouette_score']} ({res['quality']})")
                        pcols=st.columns(min(res["n_clusters"],4))
                        for i,(name,prof) in enumerate(res.get("cluster_profiles",{}).items()):
                            with pcols[i%len(pcols)]:
                                st.markdown(f"**{name}** `{prof['size']} records ({prof['pct']}%)`")
                                for cn,v in list(prof.get("means",{}).items())[:4]:
                                    st.markdown(f"<small style='color:#8b949e'>{cn}: <b style='color:#58a6ff'>{v}</b></small>",unsafe_allow_html=True)
            with t4:
                c1,c2=st.columns(2)
                tgt_f=c1.selectbox("Column",num_cols,key="ft"); periods=c2.slider("Periods",3,24,6)
                if st.button("▶ Forecast",use_container_width=True,key="fb"):
                    with st.spinner("Forecasting..."): res=ml.run_forecasting(tgt_f,periods)
                    if "error" in res: st.error(res["error"])
                    else:
                        st.success(f"{res['trend_direction']} | R²={res['r2_score']}")
                        hist=res.get("historical_values",[]); fc=res.get("forecast",[])
                        fig,ax=dfig(10,4)
                        ax.plot(range(len(hist)),hist,color="#58a6ff",linewidth=2,label="Historical")
                        ax.plot(range(len(hist),len(hist)+len(fc)),fc,color="#3fb950",linewidth=2.5,linestyle="--",label="Forecast",marker="o",markersize=5)
                        ax.axvline(x=len(hist)-1,color="#d29922",linestyle=":",alpha=.7)
                        ax.legend(framealpha=.3,labelcolor="#c9d1d9"); ax.set_title(f"Forecast: {tgt_f}",color="#e6edf3")
                        fig.tight_layout(); st.pyplot(fig); plt.close(fig)
                        fc_cols=st.columns(min(len(fc),6))
                        for i,(v,c) in enumerate(zip(fc,fc_cols)): c.metric(f"P{i+1}",v)
        except Exception as e: st.error(f"ML error: {e}")

    # ── INSIGHTS ──────────────────────────────────────
    elif page == "📢 Insights":
        ctx=f"""Dataset: {st.session_state.filename} | {sh.get('rows',0)} rows × {sh.get('columns',0)} cols
Goal: {st.session_state.goal_question or 'General analysis'} | Quality: {score}/100
Stats: {json.dumps({c:{"mean":s.get("mean"),"std":s.get("std"),"outliers":s.get("outliers",{}).get("count",0)} for c,s in list(ns.items())[:6]})}
Correlations: {json.dumps(corr.get("strong_pairs",[])[:4])}"""
        t1,t2=st.tabs(["📋 Executive Summary","📖 Data Story"])
        with t1:
            if st.button("🚀 Generate Executive Summary",use_container_width=True,type="primary"):
                with st.spinner("🤖 AI generating..."): result=ask_ai_json(f"""{ctx}
Return ONLY JSON: {{"headline":"key finding with numbers","overview":"2-3 sentences","key_findings":[{{"finding":"specific with numbers","significance":"business impact","type":"positive/negative/neutral"}}],"data_story":"4-5 sentence narrative","anomalies":["patterns"]}}""")
                if "_raw" in result: st.markdown(result["_raw"])
                else:
                    st.markdown(f"<h2 style='color:#58a6ff'>{result.get('headline','')}</h2>",unsafe_allow_html=True)
                    st.markdown(f"<p style='color:#c9d1d9;font-style:italic'>{result.get('overview','')}</p>",unsafe_allow_html=True)
                    st.markdown("---")
                    c1,c2=st.columns([1.2,1],gap="large")
                    with c1:
                        st.markdown("**🔑 Key Findings:**")
                        tc={"positive":"pos","negative":"neg","neutral":""}
                        for f in result.get("key_findings",[]):
                            cls=tc.get(f.get("type",""),"")
                            st.markdown(f'<div class="insight-item {cls}"><div class="ii-title">{f.get("finding","")}</div><div class="ii-sub">{f.get("significance","")}</div></div>',unsafe_allow_html=True)
                    with c2:
                        st.markdown("**📖 Data Story:**")
                        st.markdown(f'<p style="color:#c9d1d9;line-height:1.8">{result.get("data_story","")}</p>',unsafe_allow_html=True)
                        for a in result.get("anomalies",[]):
                            st.markdown(f'<div class="insight-item warn"><div class="ii-title">⚠️ {a}</div></div>',unsafe_allow_html=True)
        with t2:
            if st.button("🚀 Generate Data Story",use_container_width=True,type="primary"):
                with st.spinner("🤖 Writing story..."): result=ask_ai_json(f"""{ctx}
Return ONLY JSON: {{"title":"title","hook":"surprising opening","context":"background","plot":"main findings","climax":"key discovery","resolution":"what to do","key_metrics":[{{"metric":"name","value":"number","context":"meaning"}}]}}""")
                if "_raw" in result: st.markdown(result["_raw"])
                else:
                    st.markdown(f"<h2 style='color:#bc8cff'>{result.get('title','')}</h2>",unsafe_allow_html=True)
                    for sec,lbl in [("hook","🎣 Hook"),("context","📚 Context"),("plot","📈 Plot"),("climax","⚡ Climax"),("resolution","🎯 Resolution")]:
                        if result.get(sec): st.markdown(f"**{lbl}:** {result[sec]}")
                    km=result.get("key_metrics",[])
                    if km:
                        mcols=st.columns(min(len(km),4))
                        for i,(m,c) in enumerate(zip(km,mcols)): c.metric(m.get("metric",""),m.get("value",""),help=m.get("context",""))

    # ── ACTIONS ───────────────────────────────────────
    elif page == "🎯 Actions":
        ctx=f"""Dataset: {st.session_state.filename} | Goal: {st.session_state.goal_question or 'General'}
Quality: {score}/100 | Issues: {[i.get('message','') for i in qr.get('issues',[])[:3]]}
Stats: {json.dumps({c:{"mean":s.get("mean"),"outliers":s.get("outliers",{}).get("count",0)} for c,s in list(ns.items())[:5]})}"""
        if st.button("🚀 Generate Action Plan",use_container_width=True,type="primary"):
            with st.spinner("🤖 Generating..."): result=ask_ai_json(f"""{ctx}
Return ONLY JSON: {{"immediate_actions":[{{"action":"action","reason":"evidence","impact":"high/medium/low","effort":"low/medium/high","timeline":"today/week/month","kpi":"measure"}}],"strategic_recommendations":[{{"recommendation":"move","business_value":"benefit","evidence":"data"}}],"data_improvements":[{{"gap":"missing","value":"enables"}}],"watch_out":[{{"risk":"risk","indicator":"sign","threshold":"level"}}]}}""")
            if "_raw" in result: st.markdown(result["_raw"])
            else:
                st.markdown("### ⚡ Immediate Actions")
                ie={"high":"tag-high","medium":"tag-med","low":"tag-low"}
                for i,action in enumerate(result.get("immediate_actions",[]),1):
                    imp=action.get("impact","medium").lower(); eff=action.get("effort","medium").lower()
                    with st.expander(f"{'🔴' if imp=='high' else '🟡' if imp=='medium' else '🟢'} {i}. {action.get('action','')}"):
                        c1,c2,c3=st.columns(3)
                        c1.metric("Impact",action.get("impact","—").title())
                        c2.metric("Effort",action.get("effort","—").title())
                        c3.metric("Timeline",action.get("timeline","—"))
                        st.info(f"📊 **Evidence:** {action.get('reason','')}")
                        if action.get("kpi"): st.caption(f"📏 Measure: {action['kpi']}")
                c1,c2=st.columns(2,gap="large")
                with c1:
                    if result.get("strategic_recommendations"):
                        st.markdown("### 🎯 Strategic")
                        for rec in result["strategic_recommendations"]:
                            st.markdown(f'<div class="insight-item pos"><div class="ii-title">{rec.get("recommendation","")}</div><div class="ii-sub">{rec.get("business_value","")}</div><div style="color:#58a6ff;font-size:11px;margin-top:4px">{rec.get("evidence","")}</div></div>',unsafe_allow_html=True)
                with c2:
                    if result.get("watch_out"):
                        st.markdown("### 👀 Watch Out")
                        for w in result["watch_out"]:
                            st.markdown(f'<div class="insight-item warn"><div class="ii-title">{w.get("risk","")}</div><div class="ii-sub">{w.get("indicator","")}</div><div style="color:#f85149;font-size:11px;margin-top:3px">Alert: {w.get("threshold","")}</div></div>',unsafe_allow_html=True)
                if result.get("data_improvements"):
                    st.markdown("### 📈 Data Gaps")
                    for imp in result["data_improvements"]:
                        st.markdown(f'<div class="insight-item"><div class="ii-title">{imp.get("gap","")}</div><div class="ii-sub">{imp.get("value","")}</div></div>',unsafe_allow_html=True)

    # ── PREVIEW ───────────────────────────────────────
    elif page == "📋 Preview":
        st.markdown('<div class="card"><div class="card-hdr">📋 Data Preview</div>', unsafe_allow_html=True)
        c1,c2,c3=st.columns(3)
        c1.metric("Rows",f"{len(df):,}"); c2.metric("Columns",len(df.columns))
        c3.metric("Memory",f"{df.memory_usage(deep=True).sum()/1024:.1f} KB")
        st.markdown("<br>",unsafe_allow_html=True)
        n_rows=st.slider("Rows to show",10,min(500,len(df)),50)
        col_filter=st.multiselect("Columns",df.columns.tolist(),default=df.columns.tolist())
        if col_filter: st.dataframe(df[col_filter].head(n_rows),use_container_width=True,hide_index=True,height=400)
        st.markdown("**Column Info:**")
        info=[{"Column":c,"Type":str(df[c].dtype),"Non-Null":int(df[c].notna().sum()),
               "Null":int(df[c].isna().sum()),"Unique":int(df[c].nunique()),
               "Sample":str(df[c].dropna().iloc[0]) if len(df[c].dropna())>0 else "—"} for c in df.columns]
        st.dataframe(pd.DataFrame(info),use_container_width=True,hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════════
    # FIXED CHATBOT — Bottom Right FAB
    # ════════════════════════════════════════════════════
    ctx_ai = f"""Dataset: {st.session_state.filename}
Shape: {sh.get('rows',0):,} rows × {sh.get('columns',0)} cols
Columns: {', '.join(df.columns.tolist())}
Numeric: {', '.join(num_cols)} | Categorical: {', '.join(cat_cols)}
Quality: {score}/100 | Goal: {st.session_state.goal_question or 'General analysis'}
Sample:\n{df.head(3).to_string()}
Stats:\n"""+"\n".join([f"  {c}: mean={s.get('mean')}, std={s.get('std')}, outliers={s.get('outliers',{}).get('count',0)}" for c,s in list(ns.items())[:5]])

    system_ai = f"""You are DataMind AI — expert data analyst.
{ctx_ai}
Rules: Reply in Hinglish (Hindi+English). Use specific numbers from the data. Use **bold** and bullet points. Be actionable and insightful."""

    st.markdown("---")
    st.markdown("### 💬 AI Data Analyst")

    # Quick pills
    pc1,pc2,pc3,pc4 = st.columns(4)
    quick=None
    if pc1.button("📊 Summary",key="q1",use_container_width=True): quick="Dataset ka complete summary do — key numbers ke saath"
    if pc2.button("💡 Insights",key="q2",use_container_width=True): quick="Top 5 insights kya hain is data mein?"
    if pc3.button("🎯 Actions",key="q3",use_container_width=True): quick="Top 3 actionable recommendations do"
    if pc4.button("🤖 ML Suggest",key="q4",use_container_width=True): quick="Is dataset ke liye best ML model suggest karo"

    # Chat display
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history[-10:]:
            with st.chat_message(msg["role"],avatar="👤" if msg["role"]=="user" else "🤖"):
                st.markdown(msg["content"])

    user_in = st.chat_input("Kuch bhi poochho is data ke baare mein...", key="main_chat")
    if quick: user_in = quick

    if user_in:
        st.session_state.chat_history.append({"role":"user","content":user_in})
        with st.chat_message("user",avatar="👤"): st.markdown(user_in)
        with st.chat_message("assistant",avatar="🤖"):
            with st.spinner("🤖 Thinking..."):
                reply = ask_ai(user_in, system_ai, st.session_state.chat_history[:-1])
            st.markdown(reply)
        st.session_state.chat_history.append({"role":"assistant","content":reply})

    if st.session_state.chat_history:
        if st.button("🗑 Clear Chat",key="clr",use_container_width=False):
            st.session_state.chat_history=[]; st.rerun()