/**
 * DataMind Pro — Full 6-Step Workflow Frontend
 * Step 1: Ask Question | Step 2: Collect Data
 * Step 3: Clean | Step 4: Analyze
 * Step 5: Communicate | Step 6: Recommend
 */

// ─── STATE ─────────────────────────────────────────
let SESSION_ID = null;
let ANALYSIS_DATA = null;
let AVAILABLE_CHARTS = [];
let CHAT_HISTORY = [];
let CURRENT_GOAL = {};
let GOAL_TEMPLATES = {};

// ─── GLOBAL SESSION EXPIRY HANDLER ─────────────────
async function safeFetch(url, options={}) {
  const res = await fetch(url, options);
  // Only trigger expiry if: session exists AND url contains session ID AND is a data API
  const isDataApi = url.includes('/api/analysis/') || url.includes('/api/charts/') ||
                    url.includes('/api/ml/') || url.includes('/api/workflow/executive') ||
                    url.includes('/api/workflow/data-story') || url.includes('/api/workflow/recommendations') ||
                    url.includes('/api/extras/') || url.includes('/api/report/') ||
                    url.includes('/api/chat/');
  if(res.status === 404 && SESSION_ID && url.includes(SESSION_ID) && isDataApi) {
    if(!window._expiredShown) {
      window._expiredShown = true;
      showExpiredBanner();
    }
  }
  return res;
}

function showExpiredBanner() {
  var old = document.getElementById("expiredBanner");
  if(old) old.remove();
  var b = document.createElement("div");
  b.id = "expiredBanner";
  b.style.cssText = "position:fixed;top:56px;left:0;right:0;z-index:5000;background:linear-gradient(135deg,#d29922,#f59e0b);color:#000;padding:14px 24px;text-align:center;font-family:Syne,sans-serif;font-size:13px;font-weight:700;display:flex;align-items:center;justify-content:center;gap:16px;box-shadow:0 4px 20px rgba(0,0,0,.3)";
  var span = document.createElement("span");
  span.textContent = "Server restart hua — session expire ho gaya. Data dobara upload karo.";
  var btn = document.createElement("button");
  btn.textContent = "Reset";
  btn.style.cssText = "padding:7px 18px;border-radius:8px;border:none;background:#000;color:#fff;font-family:Syne,sans-serif;font-weight:700;cursor:pointer;font-size:13px";
  btn.onclick = function() {
    document.getElementById("expiredBanner").remove();
    window._expiredShown = false;
    resetApp();
  };
  b.appendChild(span);
  b.appendChild(btn);
  document.body.appendChild(b);
  setTimeout(function() {
    var el = document.getElementById("expiredBanner");
    if(el) el.remove();
    window._expiredShown = false;
    resetApp();
  }, 10000);
}

function showErrorBanner(msg) {
  var old = document.getElementById("errorBanner");
  if(old) old.remove();
  var b = document.createElement("div");
  b.id = "errorBanner";
  b.style.cssText = "position:fixed;top:56px;left:0;right:0;z-index:5000;background:linear-gradient(135deg,#f85149,#c0392b);color:#fff;padding:12px 24px;text-align:center;font-family:Syne,sans-serif;font-size:13px;font-weight:600;display:flex;align-items:center;justify-content:center;gap:16px;box-shadow:0 4px 20px rgba(0,0,0,.4)";
  var span = document.createElement("span");
  span.textContent = "❌ " + msg;
  var btn = document.createElement("button");
  btn.textContent = "✕";
  btn.style.cssText = "padding:4px 12px;border-radius:6px;border:none;background:rgba(255,255,255,.2);color:#fff;cursor:pointer;font-size:13px";
  btn.onclick = function() { document.getElementById("errorBanner").remove(); };
  b.appendChild(span);
  b.appendChild(btn);
  document.body.appendChild(b);
  setTimeout(function() { var el = document.getElementById("errorBanner"); if(el) el.remove(); }, 8000);
}

// ─── SAMPLE DATA ───────────────────────────────────
const SAMPLES = {
  sales: `month,product,category,sales,units,profit,region,target\nJan,Laptop,Electronics,145000,29,42000,North,130000\nJan,Phone,Electronics,89000,89,22000,South,80000\nJan,Shoes,Apparel,34000,113,9000,East,40000\nFeb,Laptop,Electronics,167000,33,48000,North,150000\nFeb,Phone,Electronics,95000,95,24000,West,90000\nFeb,Shoes,Apparel,41000,136,11000,South,38000\nMar,Laptop,Electronics,139000,27,40000,East,145000\nMar,TV,Electronics,78000,15,18000,North,75000\nMar,Shirt,Apparel,28000,140,7000,West,30000\nApr,Phone,Electronics,103000,103,26000,North,95000\nApr,Laptop,Electronics,188000,37,55000,South,170000\nApr,TV,Electronics,92000,18,21000,East,88000\nMay,Shoes,Apparel,52000,173,14000,North,48000\nMay,Laptop,Electronics,172000,34,50000,West,160000\nMay,Phone,Electronics,110000,110,28000,South,100000\nJun,TV,Electronics,101000,19,23000,North,95000\nJun,Shirt,Apparel,35000,175,9000,East,32000\nJun,Laptop,Electronics,195000,39,57000,West,180000`,
  employees: `id,name,department,age,salary,experience,rating,city,gender,promoted\nE001,Rahul Sharma,Engineering,28,75000,4,4.2,Delhi,M,No\nE002,Priya Patel,Marketing,32,65000,7,4.5,Mumbai,F,Yes\nE003,Amit Kumar,Engineering,35,92000,10,4.8,Bangalore,M,Yes\nE004,Sneha Gupta,HR,27,48000,3,3.9,Delhi,F,No\nE005,Vikram Singh,Engineering,30,82000,6,4.3,Hyderabad,M,No\nE006,Anita Joshi,Marketing,29,60000,5,4.1,Pune,F,No\nE007,Rajesh Verma,Finance,40,110000,15,4.6,Mumbai,M,Yes\nE008,Kavita Mehta,Engineering,26,68000,2,3.8,Bangalore,F,No\nE009,Suresh Nair,HR,33,52000,8,4.0,Chennai,M,No\nE010,Deepa Reddy,Finance,37,98000,12,4.7,Hyderabad,F,Yes\nE011,Nitin Agarwal,Engineering,31,85000,7,4.4,Delhi,M,No\nE012,Pooja Shah,Marketing,28,58000,4,3.7,Mumbai,F,No\nE013,Arun Pillai,Engineering,45,125000,20,4.9,Bangalore,M,Yes\nE014,Meera Iyer,Finance,34,88000,9,4.2,Chennai,F,Yes\nE015,Rohit Tiwari,Engineering,29,72000,5,4.1,Pune,M,No`,
  ecommerce: `order_id,customer_id,product,category,price,qty,discount,rating,delivery_days,returned\nORD001,C045,Wireless Earbuds,Electronics,2499,1,10,4.3,3,No\nORD002,C012,Cotton Kurta,Clothing,899,2,5,4.1,5,No\nORD003,C078,Python Book,Books,599,1,0,4.7,4,No\nORD004,C023,Running Shoes,Footwear,3499,1,15,3.9,6,Yes\nORD005,C056,Bluetooth Speaker,Electronics,1999,1,8,4.5,3,No\nORD006,C034,Jeans,Clothing,1299,1,10,4.0,5,No\nORD007,C089,Data Science Book,Books,799,2,0,4.8,4,No\nORD008,C011,Formal Shoes,Footwear,2999,1,5,4.2,7,No\nORD009,C067,Smart Watch,Electronics,8999,1,12,4.6,3,Yes\nORD010,C045,Yoga Mat,Sports,1499,1,0,4.4,5,No\nORD011,C023,Novel,Books,399,3,5,4.1,4,No\nORD012,C078,Sneakers,Footwear,2199,1,10,3.8,6,Yes\nORD013,C034,T-Shirt,Clothing,699,4,0,4.0,5,No\nORD014,C056,Laptop Stand,Electronics,1799,1,8,4.5,4,No\nORD015,C012,Cricket Bat,Sports,2999,1,5,4.6,7,No`
};

// ─── LOADING ───────────────────────────────────────
function showLoading(text='Processing...', pct=20, step='') {
  document.getElementById('loadingOverlay').classList.add('show');
  document.getElementById('loadingText').textContent = text;
  document.getElementById('progressFill').style.width = pct + '%';
  document.getElementById('loadingStep').textContent = step;
}
function setProgress(pct, text, step='') {
  document.getElementById('progressFill').style.width = pct + '%';
  if(text) document.getElementById('loadingText').textContent = text;
  if(step) document.getElementById('loadingStep').textContent = step;
}
function hideLoading() { setTimeout(()=>document.getElementById('loadingOverlay').classList.remove('show'),300); }

// ─── WORKFLOW STEPS UI ─────────────────────────────
function setWfStep(n) {
  var wp=document.getElementById('workflowProgress');
  if(wp) wp.style.display='flex';
  for(var i=1;i<=6;i++){
    var el=document.getElementById('wf'+i);
    if(!el) continue;
    el.className='wf-step'+(i<n?' done':(i===n?' active':''));
  }
}
function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s=>s.classList.remove('active'));
  const s=document.getElementById('screen-'+id);
  if(s){s.classList.add('active');s.scrollTop=0;}
}

// ══════════════════════════════════════════════════
// STEP 1 — ASK THE RIGHT QUESTION
// ══════════════════════════════════════════════════
async function initStep1() {
  try {
    const res = await fetch('/api/workflow/goals');
    if(res.ok) {
      const data = await res.json();
      if(data && typeof data === 'object') GOAL_TEMPLATES = data;
    }
  } catch(e) { console.warn('Goals load failed:', e.message); }
  if(!GOAL_TEMPLATES || typeof GOAL_TEMPLATES !== 'object') GOAL_TEMPLATES = {};
  setWfStep(1);
}

function selectGoal(card) {
  document.querySelectorAll('.goal-card').forEach(function(c){ c.classList.remove('selected'); });
  card.classList.add('selected');
  var type = card.dataset.type;
  CURRENT_GOAL.type = type;
  var tmpl = (GOAL_TEMPLATES && GOAL_TEMPLATES[type]) ? GOAL_TEMPLATES[type] : {};
  document.getElementById('goalForm').style.display = 'block';
  var qs = tmpl.questions || [];
  var sqEl = document.getElementById('suggestedQs');
  sqEl.innerHTML = '';
  if(qs.length) {
    var lbl = document.createElement('div');
    lbl.className = 'sug-label';
    lbl.textContent = 'Suggested questions:';
    sqEl.appendChild(lbl);
    qs.forEach(function(q) {
      var sp = document.createElement('span');
      sp.className = 'sug-q';
      sp.textContent = q;
      (function(question){ sp.onclick = function(){ document.getElementById('businessQuestion').value = question; }; })(q);
      sqEl.appendChild(sp);
    });
  }
  if(tmpl.kpis && Array.isArray(tmpl.kpis)) {
    document.getElementById('kpiInput').value = tmpl.kpis.join(', ');
  }
  document.getElementById('goalForm').scrollIntoView({behavior:'smooth', block:'nearest'});
}

function saveGoalAndNext() {
  const q = document.getElementById('businessQuestion').value.trim();
  if(!q){ showErrorBanner('Please enter your business question!'); return; }
  CURRENT_GOAL.question = q;
  CURRENT_GOAL.label = document.querySelector('.goal-card.selected h3')?.textContent || 'Custom Analysis';
  CURRENT_GOAL.kpis = document.getElementById('kpiInput').value.split(',').map(k=>k.trim()).filter(Boolean);
  CURRENT_GOAL.audience = document.getElementById('audience').value;
  CURRENT_GOAL.deadline = document.getElementById('deadline').value;
  // Show goal reminder in step 2
  document.getElementById('goalReminder').textContent = `🎯 Goal: "${q}"`;
  setWfStep(2);
  showScreen('step2');
}

// ══════════════════════════════════════════════════
// STEP 2 — COLLECT DATA
// ══════════════════════════════════════════════════

// Drag & Drop
const dropZone = document.getElementById('dropZone');
dropZone.addEventListener('dragover',e=>{e.preventDefault();dropZone.classList.add('drag-over');});
dropZone.addEventListener('dragleave',()=>dropZone.classList.remove('drag-over'));
dropZone.addEventListener('drop',e=>{e.preventDefault();dropZone.classList.remove('drag-over');const f=e.dataTransfer.files[0];if(f)uploadFile(f);});
document.getElementById('fileInput').addEventListener('change',e=>{if(e.target.files[0])uploadFile(e.target.files[0]);});

async function uploadFile(file) {
  showLoading('Uploading file...', 15, 'Reading file bytes...');
  const fd = new FormData(); fd.append('file', file);
  try {
    const res = await fetch('/api/upload/file',{method:'POST',body:fd});
    const data = await res.json();
    if(data.error){hideLoading();showErrorBanner('Upload error: ' + data.error);return;}
    await runFullPipeline(data.session_id, data.filename);
  } catch(e){hideLoading();showErrorBanner('Network error: ' + e.message);}
}

async function uploadText() {
  const text = document.getElementById('pasteArea').value.trim();
  if(!text){showErrorBanner('Please paste some CSV data!');return;}
  showLoading('Parsing CSV...', 15, 'Detecting separator...');
  try {
    const res = await fetch('/api/upload/text',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text})});
    const data = await res.json();
    if(data.error){hideLoading();showErrorBanner('Parse error: ' + data.error);return;}
    await runFullPipeline(data.session_id, data.filename);
  } catch(e){hideLoading();showErrorBanner('Network error: ' + e.message);}
}

function loadSample(type) {
  document.getElementById('pasteArea').value = SAMPLES[type];
  uploadText();
}

// ──── FULL ANALYSIS PIPELINE ───────────────────────
async function runFullPipeline(sessionId, filename) {
  SESSION_ID = sessionId;
  // Save to sessionStorage for tab refresh resilience
  try { sessionStorage.setItem('dm_session', sessionId); sessionStorage.setItem('dm_file', filename); } catch(e){}

  // Save goal to session
  if(CURRENT_GOAL.question) {
    await fetch(`/api/workflow/set-goal/${sessionId}`,{
      method:'POST', headers:{'Content-Type':'application/json'},
      body:JSON.stringify(CURRENT_GOAL)
    });
  }

  setProgress(20,'Validating dataset...','Step 2: Checking data quality');
  // Validate data for goal
  let validation = null;
  try {
    const vRes = await fetch(`/api/workflow/validate/${sessionId}`,{
      method:'POST', headers:{'Content-Type':'application/json'},
      body:JSON.stringify({goal_type: CURRENT_GOAL.type||'custom'})
    });
    validation = await vRes.json();
  } catch(e){}

  setProgress(35,'Running EDA engine...','Step 3: pandas + scipy analysis');
  const analysis = await fetchAnalysis();
  if(!analysis){return;}
  ANALYSIS_DATA = analysis;

  setProgress(60,'Generating charts...','Step 4: matplotlib + seaborn + plotly');
  await fetchCharts();

  setProgress(85,'Rendering dashboard...','Building all views...');
  renderAll(filename);

  setProgress(100,'Complete! 🎉','');
  hideLoading();

  // Show analysis screen
  document.getElementById('screen-step2').classList.remove('active');
  document.getElementById('screen-analysis').style.display = 'block';
  document.getElementById('screen-analysis').classList.add('active');
  document.getElementById('dsLabel').style.display = 'block';
  document.getElementById('dsLabel').textContent = `${filename} — ${(analysis.overview?.shape?.rows||0).toLocaleString()} × ${analysis.overview?.shape?.columns||0}`;
  document.getElementById('resetBtn').style.display = 'inline-flex';
  setWfStep(4);

  // Show validation in step 2 (for reference) and also in clean tab
  if(validation) renderValidation(validation, filename);

  addChatMsg('ai', `✅ <strong>${filename}</strong> loaded!<br>
📊 <strong>${(analysis.overview?.shape?.rows||0).toLocaleString()} rows × ${analysis.overview?.shape?.columns||0} cols</strong><br>
🔍 Quality Score: <strong>${analysis.quality_report?.quality_score}/100</strong><br>
⚠️ Issues: <strong>${analysis.quality_report?.total_issues||0}</strong><br><br>
${CURRENT_GOAL.question ? `🎯 Goal: <em>"${CURRENT_GOAL.question}"</em><br><br>`:''}
Kuch bhi poochho — main taiyaar hun! 🚀`);
}

async function fetchAnalysis() {
  for(var attempt = 1; attempt <= 2; attempt++) {
    try {
      if(attempt === 2) {
        setProgress(40, 'Retrying analysis...', 'Second attempt...');
        await new Promise(function(r){ setTimeout(r, 2000); });
      }
      var res = await safeFetch('/api/analysis/full/' + SESSION_ID);
      if(!res.ok){
        if(attempt === 2){ hideLoading(); showErrorBanner('Server error ' + res.status + ' — please re-upload dataset.'); return null; }
        continue;
      }
      var data = await res.json();
      if(!data || !data.overview){
        if(attempt === 2){ hideLoading(); showErrorBanner('Analysis returned empty — try re-uploading.'); return null; }
        continue;
      }
      return data;
    } catch(e){
      if(attempt === 2){ hideLoading(); showErrorBanner('Analysis failed: ' + e.message); return null; }
    }
  }
  return null;
}

async function fetchCharts() {
  try {
    const res = await safeFetch(`/api/charts/all/${SESSION_ID}`);
    if(!res.ok){ console.warn('Charts failed:', res.status); AVAILABLE_CHARTS = []; return; }
    const data = await res.json();
    AVAILABLE_CHARTS = (data && data.available_charts) ? data.available_charts : [];
  } catch(e){ console.warn('Charts error:', e.message); AVAILABLE_CHARTS = []; }
}

// ══════════════════════════════════════════════════
// RENDER ALL SECTIONS
// ══════════════════════════════════════════════════
function renderAll(filename) {
  renderOverview();
  renderClean();
  renderAnalyze();
  renderStats();
  renderQuality();
  renderCorrelation();
  renderPreview();
  // Steps 5 & 6 rendered on demand
  renderCommunicatePlaceholder();
  renderRecommendPlaceholder();
}

// ── OVERVIEW ────────────────────────────────────────
function renderOverview() {
  if(!ANALYSIS_DATA) { document.getElementById('overviewContent').innerHTML='<div class="card"><p style="color:var(--muted)">Analysis data not available. Please re-upload your dataset.</p></div>'; return; }
  const a=ANALYSIS_DATA, ov=a.overview||{}, sh=ov.shape||{}, mis=ov.missing||{}, dup=ov.duplicates||{}, ct=ov.column_types||{}, qr=a.quality_report||{};
  const sc=qr.quality_score||0, scC=sc>=80?'c-green':sc>=60?'c-orange':'c-red';
  document.getElementById('overviewContent').innerHTML=`
    <div class="stat-grid">
      <div class="stat-box"><div class="stat-label">Rows</div><div class="stat-val c-accent">${(sh.rows||0).toLocaleString()}</div><div class="stat-sub">observations</div></div>
      <div class="stat-box"><div class="stat-label">Columns</div><div class="stat-val c-purple">${sh.columns||0}</div><div class="stat-sub">${ct.numeric?.length||0} numeric · ${ct.categorical?.length||0} categ.</div></div>
      <div class="stat-box"><div class="stat-label">Missing</div><div class="stat-val ${mis.total_missing_cells>0?'c-orange':'c-green'}">${(mis.total_missing_cells||0).toLocaleString()}</div><div class="stat-sub">${mis.missing_percentage||0}% cells</div></div>
      <div class="stat-box"><div class="stat-label">Duplicates</div><div class="stat-val ${dup.duplicate_rows>0?'c-orange':'c-green'}">${dup.duplicate_rows||0}</div><div class="stat-sub">${dup.duplicate_percentage||0}% of rows</div></div>
      <div class="stat-box"><div class="stat-label">Quality Score</div><div class="stat-val ${scC}">${sc}</div><div class="stat-sub">out of 100</div></div>
      <div class="stat-box"><div class="stat-label">Memory</div><div class="stat-val c-muted">${ov.memory_usage_mb||0}</div><div class="stat-sub">MB in RAM</div></div>
    </div>
    ${CURRENT_GOAL.question?`<div class="card" style="background:rgba(63,185,80,.05);border-color:rgba(63,185,80,.2)">
      <div style="font-size:13px"><strong style="color:var(--green)">🎯 Analysis Goal:</strong> ${CURRENT_GOAL.question}<br>
      <span style="color:var(--muted);font-size:11px;margin-top:4px;display:block">Audience: ${CURRENT_GOAL.audience||'—'} · KPIs: ${CURRENT_GOAL.kpis?.join(', ')||'—'}</span></div>
    </div>`:''}
    <div class="card">
      <div class="card-title">🏷 Column Types</div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px">
        <div><div style="font-size:10px;color:var(--muted);font-weight:700;text-transform:uppercase;margin-bottom:8px">NUMERIC (${ct.numeric?.length||0})</div>${(ct.numeric||[]).map(c=>`<span class="tag tag-info" style="margin:2px">${c}</span>`).join('')}</div>
        <div><div style="font-size:10px;color:var(--muted);font-weight:700;text-transform:uppercase;margin-bottom:8px">CATEGORICAL (${ct.categorical?.length||0})</div>${(ct.categorical||[]).map(c=>`<span class="tag tag-purple" style="margin:2px">${c}</span>`).join('')}</div>
        <div><div style="font-size:10px;color:var(--muted);font-weight:700;text-transform:uppercase;margin-bottom:8px">DATETIME (${ct.datetime?.length||0})</div>${(ct.datetime||[]).map(c=>`<span class="tag tag-success" style="margin:2px">${c}</span>`).join('')||'<span style="color:var(--dim);font-size:12px">none</span>'}</div>
      </div>
    </div>`;
}

// ── STEP 3: CLEAN ────────────────────────────────────
function renderValidation(v, filename) {
  const sc=v.score||0, scC=sc>=80?'var(--green)':sc>=60?'var(--orange)':'var(--red)';
  const allIssues=[...v.issues.map(i=>({t:'error',m:i})),...v.warnings.map(w=>({t:'warn',m:w}))];
  document.getElementById('validationResult').style.display='block';
  document.getElementById('validationResult').innerHTML=`
    <div class="validation-card">
      <div class="val-score" style="color:${scC}">${sc}/100</div>
      <div class="val-title">Dataset suitability for: <strong>${CURRENT_GOAL.label||'Custom Analysis'}</strong></div>
      <div class="val-issues">
        ${allIssues.length===0?'<div class="val-issue ok">✅ Dataset is suitable for your analysis goal!</div>':allIssues.map(i=>`<div class="val-issue ${i.t}">${i.t==='error'?'🔴':'⚠️'} ${i.m}</div>`).join('')}
      </div>
      ${v.suggested_analyses?.length?`<div style="font-size:12px;color:var(--muted)"><strong>Suggested analyses:</strong><br>${v.suggested_analyses.map(s=>`• ${s}`).join('<br>')}</div>`:''}
    </div>`;
}

function renderClean() {
  const cols=Object.keys(ANALYSIS_DATA.overview?.dtypes||{});
  const numCols=ANALYSIS_DATA.overview?.column_types?.numeric||[];
  const colOpts=cols.map(c=>`<option value="${c}">${c}</option>`).join('');
  const numOpts=numCols.map(c=>`<option value="${c}">${c}</option>`).join('');
  const qr=ANALYSIS_DATA.quality_report||{};
  document.getElementById('cleanContent').innerHTML=`
    <div class="card" style="margin-bottom:16px">
      <div class="card-title">🔍 Data Quality Summary</div>
      <div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap">
        <div style="font-size:40px;font-weight:800;color:${(qr.quality_score||0)>=80?'var(--green)':(qr.quality_score||0)>=60?'var(--orange)':'var(--red)'}">${qr.quality_score||0}<span style="font-size:16px;color:var(--muted)">/100</span></div>
        <div style="flex:1">
          ${(qr.issues||[]).slice(0,4).map(i=>`<div class="issue-item"><div class="issue-dot" style="background:${i.severity==='critical'?'var(--red)':i.severity==='warning'?'var(--orange)':'var(--accent)'}"></div>${i.message}</div>`).join('')}
        </div>
      </div>
      ${qr.recommendations?.length?`<div style="margin-top:12px;padding-top:12px;border-top:1px solid var(--border)"><strong style="font-size:12px;color:var(--muted)">RECOMMENDATIONS:</strong><br>${qr.recommendations.map(r=>`<div style="font-size:12px;color:var(--text);padding:4px 0">→ ${r}</div>`).join('')}</div>`:''}
    </div>
    <div class="transform-grid">
      <div class="transform-card"><h4>🗑 Drop Duplicates</h4><p style="color:var(--muted);font-size:12px;margin-bottom:12px">Remove all duplicate rows</p><button class="btn-sm" onclick="runTransform('drop_duplicates',{},'r_dup')">Remove Duplicates</button><div class="tf-result" id="r_dup"></div></div>
      <div class="transform-card"><h4>❌ Drop Column</h4><div class="tf-group"><label>Column</label><select id="t_dc">${colOpts}</select></div><button class="btn-sm" onclick="runTransform('drop_column',{column:document.getElementById('t_dc').value},'r_dc')">Drop Column</button><div class="tf-result" id="r_dc"></div></div>
      <div class="transform-card"><h4>🔧 Fill Missing Values</h4><div class="tf-group"><label>Column</label><select id="t_fc">${colOpts}</select></div><div class="tf-group"><label>Method</label><select id="t_fm"><option value="mean">Mean</option><option value="median">Median</option><option value="mode">Mode</option><option value="zero">Zero</option><option value="forward">Forward Fill</option><option value="backward">Backward Fill</option></select></div><button class="btn-sm" onclick="runTransform('fill_missing',{column:document.getElementById('t_fc').value,method:document.getElementById('t_fm').value},'r_fm')">Fill Missing</button><div class="tf-result" id="r_fm"></div></div>
      <div class="transform-card"><h4>📐 Normalize Column</h4><div class="tf-group"><label>Numeric Column</label><select id="t_nc">${numOpts}</select></div><div class="tf-group"><label>Method</label><select id="t_nm"><option value="minmax">Min-Max (0-1)</option><option value="zscore">Z-Score</option><option value="log">Log (log1p)</option></select></div><button class="btn-sm" onclick="runTransform('normalize',{column:document.getElementById('t_nc').value,method:document.getElementById('t_nm').value},'r_norm')">Normalize</button><div class="tf-result" id="r_norm"></div></div>
      <div class="transform-card"><h4>✨ Create New Column</h4><div class="tf-group"><label>Column Name</label><input type="text" id="t_newname" placeholder="profit_margin"></div><div class="tf-group"><label>Expression</label><input type="text" id="t_expr" placeholder="profit / sales * 100"></div><button class="btn-sm" onclick="runTransform('create_column',{name:document.getElementById('t_newname').value,expression:document.getElementById('t_expr').value},'r_cc')">Create Column</button><div class="tf-result" id="r_cc"></div></div>
      <div class="transform-card"><h4>🔎 Filter Rows</h4><div class="tf-group"><label>Query Expression</label><input type="text" id="t_filter" placeholder="age > 25 and salary > 50000"></div><div style="font-size:11px;color:var(--muted);margin-bottom:8px">pandas .query() syntax</div><button class="btn-sm" onclick="runTransform('filter_rows',{expression:document.getElementById('t_filter').value},'r_flt')">Apply Filter</button><div class="tf-result" id="r_flt"></div></div>
      <div class="transform-card"><h4>↕ Sort Dataset</h4><div class="tf-group"><label>Column</label><select id="t_sc">${colOpts}</select></div><div class="tf-group"><label>Order</label><select id="t_so"><option value="true">Ascending</option><option value="false">Descending</option></select></div><button class="btn-sm" onclick="runTransform('sort',{column:document.getElementById('t_sc').value,ascending:document.getElementById('t_so').value==='true'},'r_srt')">Sort</button><div class="tf-result" id="r_srt"></div></div>
      <div class="transform-card"><h4>🔄 Rename Column</h4><div class="tf-group"><label>Old Name</label><select id="t_rold">${colOpts}</select></div><div class="tf-group"><label>New Name</label><input type="text" id="t_rnew" placeholder="new_column_name"></div><button class="btn-sm" onclick="runTransform('rename_column',{old_name:document.getElementById('t_rold').value,new_name:document.getElementById('t_rnew').value},'r_ren')">Rename</button><div class="tf-result" id="r_ren"></div></div>
    </div>`;
}

async function runTransform(op, params, resId) {
  const el=document.getElementById(resId);
  el.style.display='block'; el.className='tf-result'; el.textContent='Running...';
  try {
    const res=await safeFetch(`/api/analysis/transform/${SESSION_ID}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({operation:op,params})});
    const data=await res.json();
    if(data.success){
      el.className='tf-result ok'; el.textContent=`✅ Done! ${data.original_shape[0]}×${data.original_shape[1]} → ${data.new_shape[0]}×${data.new_shape[1]}`;
      const analysis=await fetchAnalysis(); if(analysis){ANALYSIS_DATA=analysis; renderAll();}
      setWfStep(3);
    } else { el.className='tf-result err'; el.textContent='❌ '+data.error; }
  } catch(e){ el.className='tf-result err'; el.textContent='❌ '+e.message; }
}

// ── STEP 4: ANALYZE ──────────────────────────────────
function renderAnalyze() {
  const staticCharts=[
    {key:'distribution_dashboard',title:'📊 Distributions (KDE + Histogram)'},
    {key:'boxplot_dashboard',title:'📦 Box Plots — Outlier Detection'},
    {key:'correlation_heatmap',title:'🔥 Correlation Heatmap (Seaborn)'},
    {key:'scatter_matrix',title:'🔵 Scatter Matrix (Pairplot)'},
    {key:'qq_plots',title:'📐 Q-Q Plots — Normality Check'},
    {key:'violin_plots',title:'🎻 Violin Plots'},
    {key:'missing_values_chart',title:'❓ Missing Values Chart'},
  ];
  let html='<div class="chart-grid">';
  staticCharts.forEach(({key,title})=>{
    if(AVAILABLE_CHARTS.includes(key)){
      html+=`<div class="chart-card"><h4>${title}</h4><img src="/api/charts/image/${SESSION_ID}/${key}" alt="${title}" loading="lazy"></div>`;
    }
  });
  if(AVAILABLE_CHARTS.includes('interactive_scatter')){
    html+=`<div class="chart-card"><h4>🔵 Interactive Scatter (Plotly)</h4><div id="plotlyScatter" style="min-height:350px;padding:8px"></div></div>`;
  }
  if(AVAILABLE_CHARTS.includes('interactive_distribution')){
    html+=`<div class="chart-card" style="grid-column:span 2"><h4>📊 Interactive Distributions (Plotly)</h4><div id="plotlyDist" style="min-height:420px;padding:8px"></div></div>`;
  }
  // Categorical charts
  const catCharts=ANALYSIS_DATA.categorical_stats?Object.keys(ANALYSIS_DATA.categorical_stats):[]; let catIdx=0;
  catCharts.slice(0,4).forEach(col=>{
    html+=`<div class="chart-card"><h4>🏷 ${col} — Category Analysis</h4><img src="/api/charts/categorical/${SESSION_ID}/${catIdx}" alt="${col}" loading="lazy"></div>`;
    catIdx++;
  });
  html+='</div>';
  document.getElementById('analyzeContent').innerHTML=html;
  if(AVAILABLE_CHARTS.includes('interactive_scatter')) loadPlotlyChart('plotlyScatter','interactive_scatter');
  if(AVAILABLE_CHARTS.includes('interactive_distribution')) loadPlotlyChart('plotlyDist','interactive_distribution');
}

async function loadPlotlyChart(id, name) {
  try {
    const res=await safeFetch(`/api/charts/image/${SESSION_ID}/${name}`);
    const data=await res.json();
    Plotly.newPlot(id,data.data,data.layout,{responsive:true,displayModeBar:true});
  } catch(e){console.error('Plotly:',e);}
}

// ── STEP 5: COMMUNICATE ───────────────────────────────
function renderCommunicatePlaceholder() {
  document.getElementById('communicateContent').innerHTML=`
    <button class="generate-btn" onclick="generateInsights()" id="genInsightsBtn">
      <span>🤖</span> Generate AI Executive Summary & Data Story
    </button>
    <div id="insightsResult"></div>`;
}

async function generateInsights() {
  const btn=document.getElementById('genInsightsBtn');
  btn.innerHTML='<span class="spinning">⚙️</span> Generating insights with Claude AI...';
  btn.disabled=true;
  setWfStep(5);
  try {
    const [sumRes, storyRes] = await Promise.all([
      fetch(`/api/workflow/executive-summary/${SESSION_ID}`),
      fetch(`/api/workflow/data-story/${SESSION_ID}`)
    ]);
    const summary=await sumRes.json();
    const story=await storyRes.json();
    renderInsightsResult(summary, story);
  } catch(e){
    document.getElementById('insightsResult').innerHTML=`<div class="card"><p style="color:var(--red)">Error: ${e.message}</p></div>`;
  }
  btn.innerHTML='<span>🔄</span> Regenerate'; btn.disabled=false;
}

function renderInsightsResult(summary, story) {
  const typeColors={positive:'var(--green)',negative:'var(--red)',neutral:'var(--accent)'};
  document.getElementById('insightsResult').innerHTML=`
    <div class="story-card">
      <div class="story-headline">"${summary.headline||'Analysis Complete'}"</div>
      <div class="story-body">${summary.overview||''}</div>
    </div>
    ${summary.key_findings?.length?`
    <div class="card">
      <div class="card-title">💡 Key Findings</div>
      <div class="findings-grid">
        ${summary.key_findings.map(f=>`
          <div class="finding-card ${f.type||'neutral'}">
            <div style="font-size:13px;font-weight:600">${f.finding}</div>
            <div class="finding-sig">${f.significance}</div>
          </div>`).join('')}
      </div>
    </div>`:''}
    ${story.title?`
    <div class="story-card">
      <div class="card-title">📖 Data Story: "${story.title}"</div>
      <div style="margin-bottom:12px">
        <div style="font-size:16px;font-weight:700;color:var(--accent);margin-bottom:8px">${story.hook||''}</div>
        <div style="font-size:13px;line-height:1.8;color:var(--muted);margin-bottom:8px">${story.context||''}</div>
        <div style="font-size:13px;line-height:1.8;margin-bottom:8px">${story.plot||''}</div>
        <div style="font-size:14px;font-weight:700;padding:12px;background:rgba(88,166,255,.08);border-radius:8px;border-left:3px solid var(--accent);margin-bottom:8px">${story.climax||''}</div>
        <div style="font-size:13px;color:var(--green)">${story.conclusion||''}</div>
      </div>
      ${story.key_metrics?.length?`<div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:12px">${story.key_metrics.map(m=>`<div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:12px;text-align:center;min-width:100px"><div style="font-size:20px;font-weight:800;color:var(--accent)">${m.value}</div><div style="font-size:11px;color:var(--muted)">${m.metric}</div><div style="font-size:10px;color:var(--dim);margin-top:2px">${m.context||''}</div></div>`).join('')}</div>`:''}
    </div>`:''}
    ${summary.limitations?.length?`<div class="card" style="background:rgba(210,153,34,.05);border-color:rgba(210,153,34,.2)"><div class="card-title">⚠️ Limitations & Caveats</div>${summary.limitations.map(l=>`<div style="font-size:13px;padding:4px 0;color:var(--muted)">→ ${l}</div>`).join('')}</div>`:''}`;
}

// ── STEP 6: RECOMMEND ─────────────────────────────────
function renderRecommendPlaceholder() {
  document.getElementById('recommendContent').innerHTML=`
    <div class="card" style="background:rgba(63,185,80,.05);border-color:rgba(63,185,80,.2);margin-bottom:16px;text-align:center;padding:16px">
      <div style="font-size:13px;color:var(--green);font-weight:700">💬 "Insight without action = useless."</div>
      <div style="font-size:12px;color:var(--muted);margin-top:4px">Turn your data findings into concrete next steps</div>
    </div>
    <button class="generate-btn" onclick="generateRecommendations()" id="genRecBtn">
      <span>🎯</span> Generate AI Action Recommendations
    </button>
    <div id="recommendResult"></div>`;
}

async function generateRecommendations() {
  const btn=document.getElementById('genRecBtn');
  btn.innerHTML='<span class="spinning">⚙️</span> Generating recommendations...';
  btn.disabled=true;
  setWfStep(6);
  try {
    const res=await safeFetch(`/api/workflow/recommendations/${SESSION_ID}`);
    const data=await res.json();
    renderRecommendResult(data);
  } catch(e){
    document.getElementById('recommendResult').innerHTML=`<div class="card"><p style="color:var(--red)">Error: ${e.message}</p></div>`;
  }
  btn.innerHTML='<span>🔄</span> Regenerate'; btn.disabled=false;
}

function renderRecommendResult(data) {
  const impactClass={high:'impact-high',medium:'impact-medium',low:'impact-low'};
  let html='';
  if(data.immediate_actions?.length){
    html+=`<div class="card"><div class="card-title">⚡ Immediate Actions (Take This Week)</div><div class="actions-list">`;
    data.immediate_actions.forEach(a=>{
      html+=`<div class="action-card">
        <div>
          <div class="action-title">${a.action}</div>
          <div class="action-reason">${a.reason}</div>
          <div class="action-metric">📏 Measure: ${a.metric||'—'}</div>
        </div>
        <div class="action-badges">
          <span class="impact-badge ${impactClass[a.impact]||'impact-low'}">Impact: ${a.impact||'—'}</span>
          <span class="impact-badge" style="background:rgba(88,166,255,.1);color:var(--accent)">Effort: ${a.effort||'—'}</span>
          <span class="timeline-badge">⏱ ${a.timeline||'—'}</span>
        </div>
      </div>`;
    });
    html+='</div></div>';
  }
  if(data.strategic_recommendations?.length){
    html+=`<div class="card"><div class="card-title">🗺 Strategic Recommendations</div>`;
    data.strategic_recommendations.forEach(r=>{
      html+=`<div style="padding:14px;background:var(--surface);border:1px solid var(--border);border-radius:10px;margin-bottom:10px">
        <div style="font-size:14px;font-weight:700;margin-bottom:6px">${r.recommendation}</div>
        <div style="font-size:12px;color:var(--green);margin-bottom:4px">💰 ${r.business_value}</div>
        <div style="font-size:12px;color:var(--muted)">📊 Evidence: ${r.data_evidence}</div>
      </div>`;
    });
    html+='</div>';
  }
  if(data.watch_out?.length){
    html+=`<div class="card" style="background:rgba(248,81,73,.05);border-color:rgba(248,81,73,.2)"><div class="card-title">🚨 Watch Out For</div>`;
    data.watch_out.forEach(w=>{html+=`<div style="font-size:13px;padding:6px 0;border-bottom:1px solid var(--border);color:var(--muted)">⚠️ ${w}</div>`;});
    html+='</div>';
  }
  if(data.next_analysis?.length){
    html+=`<div class="card"><div class="card-title">🔍 Recommended Next Analyses</div>`;
    data.next_analysis.forEach(n=>{html+=`<div style="font-size:13px;padding:6px 0;border-bottom:1px solid var(--border)">→ ${n}</div>`;});
    html+='</div>';
  }
  if(data.data_collection_gaps?.length){
    html+=`<div class="card"><div class="card-title">📥 Data Gaps to Fill</div>`;
    data.data_collection_gaps.forEach(g=>{html+=`<div style="font-size:13px;padding:6px 0;border-bottom:1px solid var(--border);color:var(--muted)">+ ${g}</div>`;});
    html+='</div>';
  }
  document.getElementById('recommendResult').innerHTML=html||'<div class="card"><p>No recommendations generated. Check your API key.</p></div>';
}

// ── STATISTICS ──────────────────────────────────────
function renderStats() {
  const ns=ANALYSIS_DATA.numeric_stats||{}, cs=ANALYSIS_DATA.categorical_stats||{}, pca=ANALYSIS_DATA.pca_summary;
  let html='';
  if(Object.keys(ns).length){
    html+=`<div class="card"><div class="card-title">📈 Numeric Statistics</div><div class="table-wrap"><table><thead><tr><th>Column</th><th>Count</th><th>Mean</th><th>Median</th><th>Std</th><th>Min</th><th>Max</th><th>Skew</th><th>Outliers</th><th>Normal?</th></tr></thead><tbody>`;
    Object.entries(ns).forEach(([col,s])=>{
      html+=`<tr><td><strong class="c-accent">${col}</strong></td><td class="mono">${(s.count||0).toLocaleString()}</td><td class="mono">${s.mean}</td><td class="mono">${s.median}</td><td class="mono">${s.std}</td><td class="mono">${s.min}</td><td class="mono">${s.max}</td>
      <td><span class="tag ${Math.abs(s.skewness)>2?'tag-danger':Math.abs(s.skewness)>1?'tag-warn':'tag-success'}">${s.skewness}</span></td>
      <td><span class="tag ${(s.outliers?.count||0)>0?'tag-warn':'tag-success'}">${s.outliers?.count||0}</span></td>
      <td>${s.normality?.is_normal?'<span class="tag tag-success">✓</span>':'<span class="tag tag-warn">✗</span>'}</td></tr>`;
    });
    html+=`</tbody></table></div></div>`;
  }
  if(Object.keys(cs).length){
    html+=`<div class="card"><div class="card-title">🏷 Categorical Statistics</div>`;
    Object.entries(cs).forEach(([col,s])=>{
      const top5=Object.entries(s.value_counts||{}).slice(0,5);
      html+=`<div style="margin-bottom:18px;padding-bottom:18px;border-bottom:1px solid var(--border)">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
          <strong class="c-accent">${col}</strong>
          <span class="tag tag-info">unique: ${s.unique_values}</span>
          <span class="tag ${s.missing>0?'tag-warn':'tag-success'}">missing: ${s.missing_pct}%</span>
          ${s.is_binary?'<span class="tag tag-purple">binary</span>':''}
        </div>
        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:6px">
          ${top5.map(([v,c])=>{const pct=s.value_percentages?.[v]||0;return`<div style="background:var(--surface);border:1px solid var(--border);border-radius:7px;padding:8px"><div style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:5px"><span>${v}</span><span class="c-accent">${c} (${pct}%)</span></div><div class="fill-bar"><div class="fill-bar-inner" style="width:${pct}%"></div></div></div>`;}).join('')}
        </div>
      </div>`;
    });
    html+='</div>';
  }
  if(pca?.available){
    html+=`<div class="card"><div class="card-title">🔬 PCA Summary</div>
    <div style="margin-bottom:10px;font-size:13px;color:var(--muted)">Components for 90% variance: <strong class="c-accent">${pca.components_for_90pct}</strong></div>
    <div style="display:flex;gap:10px;flex-wrap:wrap">${pca.explained_variance_ratio.map((v,i)=>`<div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:12px;text-align:center;min-width:80px"><div style="font-size:10px;color:var(--muted)">PC${i+1}</div><div class="c-accent" style="font-size:18px;font-weight:800">${(v*100).toFixed(1)}%</div><div style="font-size:10px;color:var(--dim)">${(pca.cumulative_variance[i]*100).toFixed(1)}% cum.</div></div>`).join('')}</div>
    </div>`;
  }
  document.getElementById('statsContent').innerHTML=html||'<div class="card"><p style="color:var(--muted)">No statistics available.</p></div>';
}

// ── QUALITY ──────────────────────────────────────────
function renderQuality() {
  const qr=ANALYSIS_DATA.quality_report||{}, sc=qr.quality_score||0;
  const scC=sc>=80?'var(--green)':sc>=60?'var(--orange)':'var(--red)';
  document.getElementById('qualityContent').innerHTML=`
    <div class="card" style="text-align:center"><div style="font-size:64px;font-weight:800;color:${scC}">${sc}</div>
    <div style="font-size:14px;color:var(--muted);margin-bottom:14px">Quality Score / 100</div>
    <div style="display:flex;justify-content:center;gap:14px">
      <span class="tag tag-danger">🔴 Critical: ${qr.summary?.critical||0}</span>
      <span class="tag tag-warn">⚠️ Warnings: ${qr.summary?.warning||0}</span>
      <span class="tag tag-info">ℹ️ Info: ${qr.summary?.info||0}</span>
    </div></div>
    <div class="card"><div class="card-title">🔍 Issues (${(qr.issues||[]).length})</div>
    ${(qr.issues||[]).length===0?'<p style="color:var(--green)">✅ No issues found!</p>':
      (qr.issues||[]).map(i=>`<div class="issue-item"><div class="issue-dot" style="background:${i.severity==='critical'?'var(--red)':i.severity==='warning'?'var(--orange)':'var(--accent)'}"></div>${i.severity==='critical'?'🔴':i.severity==='warning'?'⚠️':'ℹ️'} ${i.message}</div>`).join('')}</div>
    ${(qr.recommendations||[]).length?`<div class="card"><div class="card-title">💡 Recommendations</div>${(qr.recommendations||[]).map(r=>`<div style="padding:8px;background:var(--surface);border:1px solid var(--border);border-radius:7px;margin-bottom:7px;font-size:13px">→ ${r}</div>`).join('')}</div>`:''}`;
}

// ── CORRELATION ───────────────────────────────────────
function renderCorrelation() {
  const corr=ANALYSIS_DATA.correlations||{}, p=corr.pearson||{}, strong=corr.strong_pairs||[], cols=Object.keys(p);
  if(cols.length<2){document.getElementById('correlationContent').innerHTML='<div class="card"><p style="color:var(--muted)">Need 2+ numeric columns.</p></div>';return;}
  const cv=v=>Math.abs(v)>.7?'cv-high':Math.abs(v)>.4?'cv-mid':v<-.4?'cv-neg':'cv-low';
  document.getElementById('correlationContent').innerHTML=`
    ${strong.length?`<div class="card"><div class="card-title">💪 Strong Pairs (|r| ≥ 0.5)</div><div class="table-wrap"><table><thead><tr><th>Col 1</th><th>Col 2</th><th>r</th><th>Strength</th><th>Direction</th></tr></thead><tbody>
    ${strong.map(p=>`<tr><td class="mono c-accent">${p.col1}</td><td class="mono c-purple">${p.col2}</td><td class="mono"><strong style="color:${Math.abs(p.pearson_r)>.7?'var(--green)':'var(--orange)'}">${p.pearson_r}</strong></td><td><span class="tag ${Math.abs(p.pearson_r)>.9?'tag-success':Math.abs(p.pearson_r)>.7?'tag-info':'tag-warn'}">${p.strength}</span></td><td><span class="tag ${p.direction==='positive'?'tag-success':'tag-danger'}">${p.direction}</span></td></tr>`).join('')}
    </tbody></table></div></div>`:''}
    <div class="card"><div class="card-title">🔗 Pearson Correlation Matrix</div><div class="table-wrap"><table class="corr-table"><thead><tr><th></th>${cols.map(c=>`<th title="${c}">${c.length>8?c.slice(0,8)+'..':c}</th>`).join('')}</tr></thead><tbody>
    ${cols.map((c1,i)=>`<tr><th style="text-align:left;font-size:11px;padding:8px">${c1.length>10?c1.slice(0,10)+'..':c1}</th>${cols.map((c2,j)=>{const v=p[c1]?.[c2];return i===j?`<td>—</td>`:`<td class="corr-val ${cv(v)}">${typeof v==='number'?v.toFixed(2):'—'}</td>`;}).join('')}</tr>`).join('')}
    </tbody></table></div></div>`;
}

// ── PREVIEW ───────────────────────────────────────────
async function renderPreview() {
  try {
    const res=await safeFetch(`/api/analysis/preview/${SESSION_ID}?n=100`);
    const data=await res.json();
    const cols=data.columns||[], rows=data.data||[];
    document.getElementById('previewContent').innerHTML=`
      <div class="card" style="display:flex;justify-content:space-between;align-items:center;padding:12px 16px;margin-bottom:12px">
        <span style="color:var(--muted);font-size:13px">Showing first 100 of <strong class="c-accent">${(data.total_rows||0).toLocaleString()}</strong> rows</span>
        <div style="display:flex;gap:8px"><button class="btn-dl secondary" style="width:auto;padding:6px 14px" onclick="downloadCSV()">⬇ CSV</button><button class="btn-dl secondary" style="width:auto;padding:6px 14px" onclick="downloadExcel()">📊 Excel</button></div>
      </div>
      <div class="table-wrap"><table>
        <thead><tr><th>#</th>${cols.map(c=>`<th title="${data.dtypes?.[c]||''}">${c}<br><span style="color:var(--accent);font-size:9px">${data.dtypes?.[c]||''}</span></th>`).join('')}</tr></thead>
        <tbody>${rows.map((row,i)=>`<tr><td class="mono" style="color:var(--dim)">${i+1}</td>${cols.map(c=>`<td class="mono">${row[c]===''||row[c]==null?'<span style="color:var(--dim);font-size:9px">null</span>':row[c]}</td>`).join('')}</tr>`).join('')}</tbody>
      </table></div>`;
  } catch(e){document.getElementById('previewContent').innerHTML=`<div class="card"><p style="color:var(--red)">Error: ${e.message}</p></div>`;}
}

// ── TAB SWITCH ─────────────────────────────────────
function switchTab(tab) {
  document.querySelectorAll('.nav-item').forEach(el=>el.classList.toggle('active',el.dataset.tab===tab));
  document.querySelectorAll('.tab-panel').forEach(el=>el.classList.toggle('active',el.id===`panel-${tab}`));
}

// ── DOWNLOADS ─────────────────────────────────────
function downloadCSV()    { if(SESSION_ID) window.location.href=`/api/analysis/download/csv/${SESSION_ID}`; }
function downloadExcel()  { if(SESSION_ID) window.location.href=`/api/analysis/download/excel/${SESSION_ID}`; }
function downloadReport() { if(SESSION_ID){ addChatMsg('ai','📄 Generating PDF report...'); window.location.href=`/api/report/pdf/${SESSION_ID}`; } }

// ── CHAT ──────────────────────────────────────────
async function sendChat() {
  const input=document.getElementById('chatInput');
  const msg=input.value.trim(); if(!msg) return;
  input.value='';
  addChatMsg('user',msg); showTyping();
  if(!SESSION_ID){hideTyping();addChatMsg('ai','⚠️ Pehle data load karo!');return;}
  try {
    const res=await safeFetch(`/api/chat/message/${SESSION_ID}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg,history:CHAT_HISTORY.slice(-8)})});
    const data=await res.json(); hideTyping();
    const reply=data.reply||'Sorry, kuch error aayi.';
    addChatMsg('ai',fmtMsg(reply));
    CHAT_HISTORY.push({role:'user',content:msg});
    CHAT_HISTORY.push({role:'assistant',content:reply});
    if(CHAT_HISTORY.length>20) CHAT_HISTORY=CHAT_HISTORY.slice(-20);
    if(data.transform_result?.success){
      addChatMsg('ai',`✅ Transform! ${data.transform_result.new_shape[0]}×${data.transform_result.new_shape[1]}`);
      const analysis=await fetchAnalysis(); if(analysis){ANALYSIS_DATA=analysis;renderAll();}
    }
  } catch(e){hideTyping();addChatMsg('ai',`❌ Error: ${e.message}`);}
}
function sendQuick(q){document.getElementById('chatInput').value=q;sendChat();}
function fmtMsg(t){return t.replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>').replace(/\*(.*?)\*/g,'<em>$1</em>').replace(/```([\s\S]*?)```/g,'<pre>$1</pre>').replace(/^- (.+)$/gm,'<li>$1</li>').replace(/\n/g,'<br>');}
let typingEl=null;
function showTyping(){const m=document.getElementById('chatMsgs');typingEl=document.createElement('div');typingEl.className='chat-msg ai-msg';typingEl.id='typingMsg';typingEl.innerHTML='<div class="msg-txt"><div class="typing-dots"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div></div>';m.appendChild(typingEl);m.scrollTop=m.scrollHeight;}
function hideTyping(){document.getElementById('typingMsg')?.remove();}
function addChatMsg(role,text){const m=document.getElementById('chatMsgs');const d=document.createElement('div');d.className=`chat-msg ${role==='ai'?'ai-msg':'user-msg'}`;d.innerHTML=`<div class="msg-txt">${text}</div>`;m.appendChild(d);m.scrollTop=m.scrollHeight;}

// ── RESET ─────────────────────────────────────────
function resetApp() {
  SESSION_ID=null;ANALYSIS_DATA=null;AVAILABLE_CHARTS=[];CHAT_HISTORY=[];CURRENT_GOAL={};
  document.getElementById('screen-analysis').style.display='none';
  document.getElementById('screen-analysis').classList.remove('active');
  document.getElementById('workflowProgress').style.display='none';
  document.getElementById('dsLabel').style.display='none';
  document.getElementById('resetBtn').style.display='none';
  document.getElementById('pasteArea').value='';
  document.getElementById('fileInput').value='';
  document.getElementById('validationResult').style.display='none';
  document.querySelectorAll('.goal-card').forEach(c=>c.classList.remove('selected'));
  document.getElementById('goalForm').style.display='none';
  document.getElementById('chatMsgs').innerHTML='<div class="chat-msg ai-msg"><div class="msg-txt">👋 Reset! Naya analysis shuru karo. 🚀</div></div>';
  showScreen('step1'); setWfStep(1);
}

// ── INIT ──────────────────────────────────────────
initStep1();

// ══════════════════════════════════════════════════
// v3 FEATURES — ML, DB, EMAIL, PPT, NL-TO-CHART
// ══════════════════════════════════════════════════

// ── ML PANEL ──────────────────────────────────────
async function renderML() {
  if(!SESSION_ID){return;}
  const res = await safeFetch(`/api/ml/suggestions/${SESSION_ID}`);
  const data = await res.json();
  const numCols = data.numeric_cols || [];
  const catCols = data.categorical_cols || [];
  const allCols = [...numCols, ...catCols];
  const numOpts = numCols.map(c=>`<option value="${c}">${c}</option>`).join('');
  const catOpts = catCols.map(c=>`<option value="${c}">${c}</option>`).join('');
  const allOpts = allCols.map(c=>`<option value="${c}">${c}</option>`).join('');

  document.getElementById('mlContent').innerHTML = `
    <div class="card" style="margin-bottom:16px">
      <div class="card-title">🤖 AI Suggestions</div>
      ${(data.suggestions||[]).map(s=>`
        <div style="padding:10px;background:var(--surface);border:1px solid var(--border);border-radius:8px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center">
          <span style="font-size:13px">${s.description}</span>
          <button class="btn-sm" style="width:auto;padding:6px 14px" onclick="runMLTask('${s.task}','${s.target||''}')">Run →</button>
        </div>`).join('')}
    </div>

    <div class="transform-grid">
      <div class="transform-card">
        <h4>📈 Regression</h4>
        <p style="color:var(--muted);font-size:12px;margin-bottom:10px">Predict a numeric value</p>
        <div class="tf-group"><label>Target Column</label><select id="ml_reg_target">${numOpts}</select></div>
        <button class="btn-sm" onclick="runRegression()">Run Regression</button>
        <div class="tf-result" id="ml_reg_res"></div>
      </div>

      <div class="transform-card">
        <h4>🏷 Classification</h4>
        <p style="color:var(--muted);font-size:12px;margin-bottom:10px">Predict a category</p>
        <div class="tf-group"><label>Target Column</label><select id="ml_cls_target">${allOpts}</select></div>
        <button class="btn-sm" onclick="runClassification()">Run Classification</button>
        <div class="tf-result" id="ml_cls_res"></div>
      </div>

      <div class="transform-card">
        <h4>🔵 Clustering</h4>
        <p style="color:var(--muted);font-size:12px;margin-bottom:10px">Find natural groups (k-means)</p>
        <div class="tf-group"><label>Number of Clusters (0 = auto)</label><input type="number" id="ml_clus_n" value="0" min="0" max="10"></div>
        <button class="btn-sm" onclick="runClustering()">Run Clustering</button>
        <div class="tf-result" id="ml_clus_res"></div>
      </div>

      <div class="transform-card">
        <h4>🔮 Forecasting</h4>
        <p style="color:var(--muted);font-size:12px;margin-bottom:10px">Predict future values</p>
        <div class="tf-group"><label>Target Column</label><select id="ml_fc_target">${numOpts}</select></div>
        <div class="tf-group"><label>Forecast Periods</label><input type="number" id="ml_fc_periods" value="6" min="1" max="24"></div>
        <button class="btn-sm" onclick="runForecasting()">Run Forecast</button>
        <div class="tf-result" id="ml_fc_res"></div>
      </div>
    </div>

    <div id="mlResultFull"></div>`;
}

async function runMLTask(task, target) {
  if(task==='regression') { document.getElementById('ml_reg_target').value=target; runRegression(); }
  else if(task==='classification') { document.getElementById('ml_cls_target').value=target; runClassification(); }
  else if(task==='forecasting') { document.getElementById('ml_fc_target').value=target; runForecasting(); }
  else if(task==='clustering') { runClustering(); }
}

async function runRegression() {
  const target = document.getElementById('ml_reg_target').value;
  setMLLoading('ml_reg_res','Running regression models...');
  const res = await safeFetch(`/api/ml/regression/${SESSION_ID}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({target})});
  const data = await res.json();
  showMLResult(data, 'ml_reg_res');
}

async function runClassification() {
  const target = document.getElementById('ml_cls_target').value;
  setMLLoading('ml_cls_res','Training classifiers...');
  const res = await safeFetch(`/api/ml/classification/${SESSION_ID}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({target})});
  const data = await res.json();
  showMLResult(data, 'ml_cls_res');
}

async function runClustering() {
  const n = parseInt(document.getElementById('ml_clus_n').value)||null;
  setMLLoading('ml_clus_res','Finding clusters...');
  const res = await safeFetch(`/api/ml/clustering/${SESSION_ID}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({n_clusters:n||null})});
  const data = await res.json();
  showMLResult(data, 'ml_clus_res');
}

async function runForecasting() {
  const target = document.getElementById('ml_fc_target').value;
  const periods = parseInt(document.getElementById('ml_fc_periods').value)||6;
  setMLLoading('ml_fc_res','Forecasting...');
  const res = await safeFetch(`/api/ml/forecasting/${SESSION_ID}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({target,periods})});
  const data = await res.json();
  showMLForecast(data);
}

function setMLLoading(id,msg){const el=document.getElementById(id);el.style.display='block';el.className='tf-result';el.textContent=msg;}

function showMLResult(data, resId) {
  const el = document.getElementById(resId);
  if(data.error){el.className='tf-result err';el.style.display='block';el.textContent='❌ '+data.error;return;}
  el.style.display='block';el.className='tf-result ok';

  if(data.task==='regression'){
    let html=`✅ Best: ${data.best_model} (R²=${data.best_r2})\n`;
    Object.entries(data.model_results||{}).forEach(([m,r])=>{
      if(!r.error) html+=`  ${m}: R²=${r.r2}, RMSE=${r.rmse}\n`;
    });
    el.textContent=html;
    renderFeatureImportance(data);
  } else if(data.task==='classification'){
    el.textContent=`✅ Best: ${data.best_model} — ${data.best_accuracy}% accuracy`;
    renderFeatureImportance(data);
  } else if(data.task==='clustering'){
    el.textContent=`✅ ${data.n_clusters} clusters found. Silhouette=${data.silhouette_score} (${data.quality})`;
    renderClusterProfiles(data);
  }
}

function renderFeatureImportance(data) {
  const imp = data.feature_importance;
  if(!imp || Object.keys(imp).length===0) return;
  const container = document.getElementById('mlResultFull');
  const entries = Object.entries(imp).slice(0,8);
  const max = entries[0][1];
  container.innerHTML += `
    <div class="card" style="margin-top:16px">
      <div class="card-title">📊 Feature Importance — ${data.target}</div>
      <div style="font-size:12px;color:var(--muted);margin-bottom:10px">${data.interpretation||''}</div>
      ${entries.map(([col,val])=>`
        <div style="margin-bottom:8px">
          <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:3px">
            <span class="c-accent">${col}</span><span class="mono">${val}</span>
          </div>
          <div class="fill-bar"><div class="fill-bar-inner" style="width:${(val/max*100).toFixed(0)}%"></div></div>
        </div>`).join('')}
    </div>`;
}

function renderClusterProfiles(data) {
  const profiles = data.cluster_profiles || {};
  const container = document.getElementById('mlResultFull');
  container.innerHTML += `
    <div class="card" style="margin-top:16px">
      <div class="card-title">🔵 Cluster Profiles</div>
      <div style="font-size:12px;color:var(--muted);margin-bottom:12px">${data.interpretation||''}</div>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px">
        ${Object.entries(profiles).map(([name,p],i)=>`
          <div style="background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:14px">
            <div style="font-weight:700;color:var(--accent);margin-bottom:6px">${name}</div>
            <div style="font-size:11px;color:var(--muted);margin-bottom:8px">${p.size} records (${p.pct}%)</div>
            ${Object.entries(p.means||{}).map(([col,val])=>`<div style="font-size:11px;display:flex;justify-content:space-between;padding:2px 0;border-bottom:1px solid var(--border)"><span style="color:var(--muted)">${col}</span><span class="mono">${val}</span></div>`).join('')}
          </div>`).join('')}
      </div>
    </div>`;
}

function showMLForecast(data) {
  const el = document.getElementById('ml_fc_res');
  if(data.error){el.className='tf-result err';el.style.display='block';el.textContent='❌ '+data.error;return;}
  el.style.display='block';el.className='tf-result ok';
  el.textContent=`✅ ${data.trend_direction} | R²=${data.r2_score}`;

  const container = document.getElementById('mlResultFull');
  const forecast = data.forecast||[];
  container.innerHTML += `
    <div class="card" style="margin-top:16px">
      <div class="card-title">🔮 Forecast: ${data.target}</div>
      <div style="font-size:12px;color:var(--muted);margin-bottom:12px">${data.interpretation}</div>
      <div style="display:flex;gap:10px;flex-wrap:wrap">
        ${forecast.map((v,i)=>`<div style="background:var(--surface);border:1px solid rgba(88,166,255,.2);border-radius:8px;padding:12px;text-align:center;min-width:80px"><div style="font-size:10px;color:var(--muted)">Period ${i+1}</div><div class="c-accent" style="font-size:20px;font-weight:800">${v}</div></div>`).join('')}
      </div>
    </div>`;
}

// ── NL TO CHART ────────────────────────────────────
async function renderNLChart() {
  document.getElementById('nlChartContent').innerHTML = `
    <div class="card">
      <div class="card-title">🖼️ Natural Language to Chart</div>
      <p style="color:var(--muted);font-size:13px;margin-bottom:16px">Hinglish mein bolo — AI chart bana dega!</p>
      <div style="display:flex;gap:10px;margin-bottom:12px">
        <input type="text" id="nlInput" placeholder="e.g. 'sales ka bar chart banao' or 'scatter plot age vs salary'" style="flex:1;padding:10px 14px;background:var(--surface);border:1px solid var(--border);border-radius:9px;color:var(--text);font-family:Syne,sans-serif;font-size:13px;outline:none">
        <button class="btn-primary" onclick="generateNLChart()">Generate Chart ⚡</button>
      </div>
      <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:16px">
        <span class="pill" onclick="setNL('bar chart banao category wise sales')">📊 Category bar</span>
        <span class="pill" onclick="setNL('scatter plot banao')">🔵 Scatter plot</span>
        <span class="pill" onclick="setNL('pie chart distribution dikhao')">🥧 Pie chart</span>
        <span class="pill" onclick="setNL('histogram banao pehle numeric column ka')">📉 Histogram</span>
        <span class="pill" onclick="setNL('line chart trend dikhao')">📈 Line trend</span>
      </div>
      <div id="nlChartResult"></div>
    </div>`;
}

function setNL(text){document.getElementById('nlInput').value=text;}

async function generateNLChart() {
  const req = document.getElementById('nlInput').value.trim();
  if(!req){showErrorBanner('Kuch toh type karo!');return;}
  const res_el = document.getElementById('nlChartResult');
  res_el.innerHTML='<div style="color:var(--muted);padding:20px;text-align:center">⚙️ Generating chart...</div>';
  try {
    const res = await safeFetch(`/api/extras/nl-chart/${SESSION_ID}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({request:req})});
    const data = await res.json();
    if(data.error){res_el.innerHTML=`<div style="color:var(--red)">${data.error}</div>`;return;}
    res_el.innerHTML=`
      <div style="margin-bottom:8px;font-size:12px;color:var(--muted)">Type: <strong class="c-accent">${data.spec?.chart_type}</strong> | X: <strong>${data.spec?.x_col||'—'}</strong> | Y: <strong>${data.spec?.y_col||'—'}</strong></div>
      <img src="${data.chart}" style="width:100%;border-radius:8px">`;
  } catch(e){res_el.innerHTML=`<div style="color:var(--red)">Error: ${e.message}</div>`;}
}

// ── DB CONNECT ─────────────────────────────────────
function renderDBConnect() {
  document.getElementById('dbContent').innerHTML = `
    <div class="card">
      <div class="card-title">🗄️ Database Connection</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px">
        <div class="tf-group"><label>Database Type</label>
          <select id="db_type" onchange="toggleDBFields()">
            <option value="sqlite">SQLite (local file)</option>
            <option value="mysql">MySQL</option>
            <option value="postgresql">PostgreSQL</option>
          </select>
        </div>
        <div class="tf-group" id="db_host_group"><label>Host</label><input type="text" id="db_host" value="localhost"></div>
      </div>
      <div id="db_auth_fields" style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:12px;margin-bottom:16px">
        <div class="tf-group"><label>Port</label><input type="number" id="db_port" value="3306"></div>
        <div class="tf-group"><label>Database</label><input type="text" id="db_name" placeholder="mydb"></div>
        <div class="tf-group"><label>Username</label><input type="text" id="db_user" value="root"></div>
        <div class="tf-group"><label>Password</label><input type="password" id="db_pass"></div>
      </div>
      <div id="db_sqlite_fields" style="display:none;margin-bottom:16px">
        <div class="tf-group"><label>SQLite File Path</label><input type="text" id="db_path" placeholder="C:/path/to/database.db"></div>
      </div>
      <div style="display:flex;gap:10px">
        <button class="btn-primary" onclick="testDBConnection()">🔌 Test Connection</button>
        <button class="btn-primary" onclick="loadDBTables()" style="background:linear-gradient(135deg,var(--green),#059669)">📋 Load Tables</button>
      </div>
      <div id="db_result" style="margin-top:12px"></div>
      <div id="db_tables" style="margin-top:12px"></div>
    </div>`;
}

function toggleDBFields(){
  const t=document.getElementById('db_type').value;
  document.getElementById('db_auth_fields').style.display=t==='sqlite'?'none':'grid';
  document.getElementById('db_sqlite_fields').style.display=t==='sqlite'?'block':'none';
  if(t==='postgresql') document.getElementById('db_port').value='5432';
  else if(t==='mysql') document.getElementById('db_port').value='3306';
}

function getDBConfig(){
  const t=document.getElementById('db_type').value;
  if(t==='sqlite') return {path:document.getElementById('db_path').value||':memory:'};
  return {host:document.getElementById('db_host').value,port:parseInt(document.getElementById('db_port').value),
    database:document.getElementById('db_name').value,user:document.getElementById('db_user').value,
    password:document.getElementById('db_pass').value};
}

async function testDBConnection(){
  const res=await fetch('/api/extras/db/test',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({db_type:document.getElementById('db_type').value,config:getDBConfig()})});
  const data=await res.json();
  const el=document.getElementById('db_result');
  el.innerHTML=`<div style="padding:10px;border-radius:8px;font-size:13px;background:${data.success?'rgba(63,185,80,.08)':'rgba(248,81,73,.08)'};border:1px solid ${data.success?'var(--green)':'var(--red)'};">${data.success?'✅ '+data.message:'❌ '+data.error}</div>`;
}

async function loadDBTables(){
  const res=await fetch('/api/extras/db/tables',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({db_type:document.getElementById('db_type').value,config:getDBConfig()})});
  const data=await res.json();
  if(!data.success){document.getElementById('db_tables').innerHTML=`<p style="color:var(--red)">${data.error}</p>`;return;}
  document.getElementById('db_tables').innerHTML=`
    <div class="card-title" style="margin-top:8px">Tables Found (${data.tables.length})</div>
    <div style="display:flex;flex-wrap:wrap;gap:8px">
      ${data.tables.map(t=>`<button class="btn-sample" onclick="loadDBTable('${t}')">${t}</button>`).join('')}
    </div>`;
}

async function loadDBTable(table){
  showLoading(`Loading table: ${table}`,20,'Reading from database...');
  const res=await fetch('/api/extras/db/load',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({db_type:document.getElementById('db_type').value,config:getDBConfig(),table})});
  const data=await res.json();
  if(data.error){hideLoading();showErrorBanner('Error: ' + data.error);return;}
  await runFullPipeline(data.session_id, data.filename);
}

// ── EMAIL REPORT ────────────────────────────────────
function renderEmailSection() {
  return `
    <div class="card" style="margin-bottom:16px">
      <div class="card-title">📧 Email Report</div>
      <div style="display:flex;gap:10px;align-items:flex-end">
        <div class="tf-group" style="flex:1;margin:0">
          <label>Email Address</label>
          <input type="email" id="emailAddr" placeholder="recipient@example.com">
        </div>
        <button class="btn-primary" onclick="sendEmail()">📤 Send PDF Report</button>
      </div>
      <div id="emailResult" style="margin-top:10px"></div>
      <div style="margin-top:10px;font-size:11px;color:var(--muted)">
        ⚙️ Configure in .env: EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_SMTP, EMAIL_PORT
      </div>
    </div>`;
}

async function sendEmail(){
  const email=document.getElementById('emailAddr').value.trim();
  if(!email){showErrorBanner('Email address enter karo!');return;}
  const el=document.getElementById('emailResult');
  el.innerHTML='<span style="color:var(--muted)">📤 Sending...</span>';
  const res=await safeFetch(`/api/extras/email/${SESSION_ID}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email})});
  const data=await res.json();
  el.innerHTML=`<div style="font-size:13px;color:${data.success?'var(--green)':'var(--red)'}">${data.success?'✅ '+data.message:'❌ '+data.error}</div>`;
}

// ── LOGIN/REGISTER ──────────────────────────────────
async function checkAuth(){
  try {
    const res=await fetch('/api/auth/me',{credentials:'include'});
    const data=await res.json();
    if(data.logged_in){
      document.getElementById('userBadge').textContent='👤 '+data.username;
      document.getElementById('userBadge').style.display='inline-block';
      document.getElementById('loginBtn').style.display='none';
    } else {
      // Show login modal automatically on first visit
      setTimeout(()=>showLoginModal(), 800);
    }
  } catch(e){
    setTimeout(()=>showLoginModal(), 800);
  }
}

async function showLoginModal(){
  const modal=document.getElementById('loginModal');
  modal.style.display='flex';
}

function hideLoginModal(){document.getElementById('loginModal').style.display='none';}

async function doLogin(){
  const u=document.getElementById('loginUser').value.trim();
  const p=document.getElementById('loginPass').value;
  const res=await fetch('/api/auth/login',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:u,password:p})});
  const data=await res.json();
  if(data.success){hideLoginModal();document.getElementById('userBadge').textContent='👤 '+data.username;document.getElementById('userBadge').style.display='inline-block';document.getElementById('loginBtn').style.display='none';}
  else document.getElementById('loginError').textContent=data.error;
}

async function doRegister(){
  const u=document.getElementById('loginUser').value.trim();
  const p=document.getElementById('loginPass').value;
  const res=await fetch('/api/auth/register',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:u,password:p})});
  const data=await res.json();
  if(data.success){hideLoginModal();document.getElementById('userBadge').textContent='👤 '+data.username;document.getElementById('userBadge').style.display='inline-block';document.getElementById('loginBtn').style.display='none';}
  else document.getElementById('loginError').textContent=data.error;
}

async function doLogout(){
  await fetch('/api/auth/logout',{method:'POST',credentials:'include'});
  document.getElementById('userBadge').style.display='none';
  document.getElementById('loginBtn').style.display='inline-flex';
}

// Override switchTab for v3 panels — NO recursion
function switchTab(tab) {
  document.querySelectorAll('.nav-item').forEach(el=>
    el.classList.toggle('active',el.dataset.tab===tab));
  document.querySelectorAll('.tab-panel').forEach(el=>
    el.classList.toggle('active',el.id===`panel-${tab}`));
  if(tab==='ml' && SESSION_ID) renderML();
  if(tab==='nlchart' && SESSION_ID) renderNLChart();
  if(tab==='dbconnect') renderDBConnect();
}

// Check auth on load
checkAuth();

function downloadPPT() {
  if(SESSION_ID){ addChatMsg('ai','📽️ Generating PowerPoint...'); window.location.href='/api/extras/ppt/'+SESSION_ID; }
}

// ─── KEEP ALIVE — ping server + session every 8 min ───
setInterval(async function() {
  try { await fetch('/api/auth/me', {credentials:'include'}); } catch(e) {}
  try {
    if(SESSION_ID) await fetch('/api/analysis/full/' + SESSION_ID + '?ping=1');
  } catch(e) {}
}, 8 * 60 * 1000);