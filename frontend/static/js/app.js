/**
 * DataMind Pro — Frontend App
 * Handles all API communication and UI rendering
 */

// ─── STATE ──────────────────────────────────────────────────────────
let SESSION_ID = null;
let ANALYSIS_DATA = null;
let AVAILABLE_CHARTS = [];
let CHAT_HISTORY = [];

// ─── SAMPLE DATA ────────────────────────────────────────────────────
const SAMPLES = {
  sales: `month,product,category,sales,units,profit,region,target
Jan,Laptop,Electronics,145000,29,42000,North,130000
Jan,Phone,Electronics,89000,89,22000,South,80000
Jan,Shoes,Apparel,34000,113,9000,East,40000
Feb,Laptop,Electronics,167000,33,48000,North,150000
Feb,Phone,Electronics,95000,95,24000,West,90000
Feb,Shoes,Apparel,41000,136,11000,South,38000
Mar,Laptop,Electronics,139000,27,40000,East,145000
Mar,TV,Electronics,78000,15,18000,North,75000
Mar,Shirt,Apparel,28000,140,7000,West,30000
Apr,Phone,Electronics,103000,103,26000,North,95000
Apr,Laptop,Electronics,188000,37,55000,South,170000
Apr,TV,Electronics,92000,18,21000,East,88000
May,Shoes,Apparel,52000,173,14000,North,48000
May,Laptop,Electronics,172000,34,50000,West,160000
May,Phone,Electronics,110000,110,28000,South,100000
Jun,TV,Electronics,101000,19,23000,North,95000
Jun,Shirt,Apparel,35000,175,9000,East,32000
Jun,Laptop,Electronics,195000,39,57000,West,180000`,

  employees: `id,name,department,age,salary,experience,rating,city,gender,promoted
E001,Rahul Sharma,Engineering,28,75000,4,4.2,Delhi,M,No
E002,Priya Patel,Marketing,32,65000,7,4.5,Mumbai,F,Yes
E003,Amit Kumar,Engineering,35,92000,10,4.8,Bangalore,M,Yes
E004,Sneha Gupta,HR,27,48000,3,3.9,Delhi,F,No
E005,Vikram Singh,Engineering,30,82000,6,4.3,Hyderabad,M,No
E006,Anita Joshi,Marketing,29,60000,5,4.1,Pune,F,No
E007,Rajesh Verma,Finance,40,110000,15,4.6,Mumbai,M,Yes
E008,Kavita Mehta,Engineering,26,68000,2,3.8,Bangalore,F,No
E009,Suresh Nair,HR,33,52000,8,4.0,Chennai,M,No
E010,Deepa Reddy,Finance,37,98000,12,4.7,Hyderabad,F,Yes
E011,Nitin Agarwal,Engineering,31,85000,7,4.4,Delhi,M,No
E012,Pooja Shah,Marketing,28,58000,4,3.7,Mumbai,F,No
E013,Arun Pillai,Engineering,45,125000,20,4.9,Bangalore,M,Yes
E014,Meera Iyer,Finance,34,88000,9,4.2,Chennai,F,Yes
E015,Rohit Tiwari,Engineering,29,72000,5,4.1,Pune,M,No`,

  ecommerce: `order_id,customer_id,product,category,price,qty,discount,rating,delivery_days,returned
ORD001,C045,Wireless Earbuds,Electronics,2499,1,10,4.3,3,No
ORD002,C012,Cotton Kurta,Clothing,899,2,5,4.1,5,No
ORD003,C078,Python Book,Books,599,1,0,4.7,4,No
ORD004,C023,Running Shoes,Footwear,3499,1,15,3.9,6,Yes
ORD005,C056,Bluetooth Speaker,Electronics,1999,1,8,4.5,3,No
ORD006,C034,Jeans,Clothing,1299,1,10,4.0,5,No
ORD007,C089,Data Science Book,Books,799,2,0,4.8,4,No
ORD008,C011,Formal Shoes,Footwear,2999,1,5,4.2,7,No
ORD009,C067,Smart Watch,Electronics,8999,1,12,4.6,3,Yes
ORD010,C045,Yoga Mat,Sports,1499,1,0,4.4,5,No
ORD011,C023,Novel,Books,399,3,5,4.1,4,No
ORD012,C078,Sneakers,Footwear,2199,1,10,3.8,6,Yes
ORD013,C034,T-Shirt,Clothing,699,4,0,4.0,5,No
ORD014,C056,Laptop Stand,Electronics,1799,1,8,4.5,4,No
ORD015,C012,Cricket Bat,Sports,2999,1,5,4.6,7,No`
};

// ─── LOADING ────────────────────────────────────────────────────────
function showLoading(text = "Processing...", pct = 20) {
  document.getElementById("loadingOverlay").classList.add("show");
  document.getElementById("loadingText").textContent = text;
  document.getElementById("progressFill").style.width = pct + "%";
}
function setProgress(pct, text) {
  document.getElementById("progressFill").style.width = pct + "%";
  if (text) document.getElementById("loadingText").textContent = text;
}
function hideLoading() {
  setTimeout(() => document.getElementById("loadingOverlay").classList.remove("show"), 300);
}

// ─── DRAG & DROP ────────────────────────────────────────────────────
const dropZone = document.getElementById("dropZone");
dropZone.addEventListener("dragover", e => { e.preventDefault(); dropZone.classList.add("drag-over"); });
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("drag-over"));
dropZone.addEventListener("drop", e => {
  e.preventDefault(); dropZone.classList.remove("drag-over");
  const file = e.dataTransfer.files[0];
  if (file) uploadFile(file);
});
document.getElementById("fileInput").addEventListener("change", e => {
  if (e.target.files[0]) uploadFile(e.target.files[0]);
});

// ─── FILE UPLOAD ────────────────────────────────────────────────────
async function uploadFile(file) {
  showLoading("Uploading file...", 15);
  const formData = new FormData();
  formData.append("file", file);
  try {
    const res = await fetch("/api/upload/file", { method: "POST", body: formData });
    const data = await res.json();
    if (data.error) { hideLoading(); alert("Upload error: " + data.error); return; }
    await startAnalysis(data.session_id, data.filename);
  } catch (e) { hideLoading(); alert("Network error. Is the Flask server running?"); }
}

async function uploadText() {
  const text = document.getElementById("pasteArea").value.trim();
  if (!text) { alert("Please paste some CSV data first!"); return; }
  showLoading("Parsing CSV...", 15);
  try {
    const res = await fetch("/api/upload/text", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });
    const data = await res.json();
    if (data.error) { hideLoading(); alert("Parse error: " + data.error); return; }
    await startAnalysis(data.session_id, data.filename);
  } catch (e) { hideLoading(); alert("Network error. Is the Flask server running?"); }
}

function loadSample(type) {
  document.getElementById("pasteArea").value = SAMPLES[type];
  uploadText();
}

// ─── ANALYSIS PIPELINE ──────────────────────────────────────────────
async function startAnalysis(sessionId, filename) {
  SESSION_ID = sessionId;

  document.getElementById("dsLabel").textContent = `${filename} — loading...`;
  document.getElementById("datasetBadge").style.display = "block";
  document.getElementById("resetBtn").style.display = "inline-flex";

  setProgress(25, "Running EDA engine...");
  const analysis = await fetchAnalysis();
  if (!analysis) return;
  ANALYSIS_DATA = analysis;

  setProgress(50, "Generating charts...");
  await fetchCharts();

  setProgress(75, "Building reports...");
  renderAll(filename);

  setProgress(100, "Complete!");
  hideLoading();

  document.getElementById("uploadScreen").style.display = "none";
  document.getElementById("analysisScreen").style.display = "block";

  const shape = analysis.overview?.shape;
  document.getElementById("dsLabel").textContent =
    `${filename} — ${(shape?.rows || 0).toLocaleString()} rows × ${shape?.columns || 0} cols`;

  addChatMsg("ai", `✅ Dataset <strong>${filename}</strong> loaded and analyzed!<br><br>` +
    `📊 <strong>${(shape?.rows||0).toLocaleString()} rows</strong> × <strong>${shape?.columns||0} columns</strong><br>` +
    `🔍 Quality Score: <strong>${analysis.quality_report?.quality_score}/100</strong><br>` +
    `⚠️ Issues found: <strong>${analysis.quality_report?.total_issues || 0}</strong><br><br>` +
    `Kuch bhi poochho — main taiyaar hun! 🚀`);
}

async function fetchAnalysis() {
  try {
    const res = await fetch(`/api/analysis/full/${SESSION_ID}`);
    return await res.json();
  } catch (e) { hideLoading(); alert("Analysis failed: " + e.message); return null; }
}

async function fetchCharts() {
  try {
    const res = await fetch(`/api/charts/all/${SESSION_ID}`);
    const data = await res.json();
    AVAILABLE_CHARTS = data.available_charts || [];
  } catch (e) { console.error("Charts failed:", e); }
}

// ─── RENDER ALL SECTIONS ────────────────────────────────────────────
function renderAll(filename) {
  renderOverview();
  renderEDA();
  renderStats();
  renderQuality();
  renderCorrelation();
  renderTransform();
  renderPreview();
}

// ─── OVERVIEW ───────────────────────────────────────────────────────
function renderOverview() {
  const a = ANALYSIS_DATA;
  const ov = a.overview || {};
  const shape = ov.shape || {};
  const missing = ov.missing || {};
  const dups = ov.duplicates || {};
  const ct = ov.column_types || {};
  const qr = a.quality_report || {};

  const scoreColor = qr.quality_score >= 80 ? "c-green" : qr.quality_score >= 60 ? "c-orange" : "c-red";

  document.getElementById("overviewContent").innerHTML = `
    <div class="stat-grid">
      <div class="stat-box"><div class="stat-label">Total Rows</div><div class="stat-val c-accent">${(shape.rows||0).toLocaleString()}</div><div class="stat-sub">observations</div></div>
      <div class="stat-box"><div class="stat-label">Columns</div><div class="stat-val c-purple">${shape.columns||0}</div><div class="stat-sub">${ct.numeric?.length||0} numeric, ${ct.categorical?.length||0} categorical</div></div>
      <div class="stat-box"><div class="stat-label">Missing Cells</div><div class="stat-val ${missing.total_missing_cells>0?'c-orange':'c-green'}">${(missing.total_missing_cells||0).toLocaleString()}</div><div class="stat-sub">${missing.missing_percentage||0}% of all cells</div></div>
      <div class="stat-box"><div class="stat-label">Duplicate Rows</div><div class="stat-val ${dups.duplicate_rows>0?'c-orange':'c-green'}">${dups.duplicate_rows||0}</div><div class="stat-sub">${dups.duplicate_percentage||0}% of rows</div></div>
      <div class="stat-box"><div class="stat-label">Data Quality</div><div class="stat-val ${scoreColor}">${qr.quality_score||0}</div><div class="stat-sub">out of 100</div></div>
      <div class="stat-box"><div class="stat-label">Memory Usage</div><div class="stat-val c-muted">${ov.memory_usage_mb||0} MB</div><div class="stat-sub">in-memory</div></div>
    </div>

    <div class="card">
      <div class="card-title"><span class="icon">🏷</span>Column Types</div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px">
        <div>
          <div style="font-size:11px;color:var(--muted);font-weight:700;margin-bottom:8px">NUMERIC (${ct.numeric?.length||0})</div>
          ${(ct.numeric||[]).map(c=>`<span class="tag tag-info" style="margin:2px">${c}</span>`).join("")}
        </div>
        <div>
          <div style="font-size:11px;color:var(--muted);font-weight:700;margin-bottom:8px">CATEGORICAL (${ct.categorical?.length||0})</div>
          ${(ct.categorical||[]).map(c=>`<span class="tag tag-purple" style="margin:2px">${c}</span>`).join("")}
        </div>
        <div>
          <div style="font-size:11px;color:var(--muted);font-weight:700;margin-bottom:8px">DATETIME (${ct.datetime?.length||0})</div>
          ${(ct.datetime||[]).map(c=>`<span class="tag tag-success" style="margin:2px">${c}</span>`).join("") || '<span style="color:var(--dim);font-size:12px">none detected</span>'}
        </div>
      </div>
    </div>

    ${Object.keys(missing.columns_with_missing||{}).length > 0 ? `
    <div class="card">
      <div class="card-title"><span class="icon">❓</span>Missing Values by Column</div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Column</th><th>Missing Count</th><th>Missing %</th><th>Fill Rate</th></tr></thead>
          <tbody>
            ${Object.entries(missing.columns_with_missing||{}).map(([col,info])=>`
              <tr>
                <td class="mono">${col}</td>
                <td class="mono">${info.count.toLocaleString()}</td>
                <td><span class="tag ${info.percentage>30?'tag-danger':info.percentage>10?'tag-warn':'tag-info'}">${info.percentage}%</span></td>
                <td>
                  <div class="fill-bar-wrap">
                    <div class="fill-bar"><div class="fill-bar-inner" style="width:${100-info.percentage}%"></div></div>
                    <span style="font-size:11px;color:var(--muted)">${(100-info.percentage).toFixed(1)}%</span>
                  </div>
                </td>
              </tr>`).join("")}
          </tbody>
        </table>
      </div>
    </div>` : '<div class="card"><div style="color:var(--green);font-size:14px;text-align:center;padding:20px">✅ No missing values! Dataset is complete.</div></div>'}
  `;
}

// ─── EDA CHARTS ─────────────────────────────────────────────────────
function renderEDA() {
  const staticCharts = [
    { key: "distribution_dashboard", title: "📊 Distributions (KDE + Histogram)" },
    { key: "boxplot_dashboard", title: "📦 Box Plots — Outlier Detection" },
    { key: "correlation_heatmap", title: "🔥 Correlation Heatmap (Seaborn)" },
    { key: "scatter_matrix", title: "🔵 Scatter Matrix (Pairplot)" },
    { key: "qq_plots", title: "📐 Q-Q Plots — Normality Check" },
    { key: "violin_plots", title: "🎻 Violin Plots" },
    { key: "missing_values_chart", title: "❓ Missing Values Visualization" },
  ];

  let html = '<div class="chart-grid">';

  staticCharts.forEach(({ key, title }) => {
    if (AVAILABLE_CHARTS.includes(key)) {
      html += `
        <div class="chart-card">
          <h4>${title}</h4>
          <img src="/api/charts/image/${SESSION_ID}/${key}" alt="${title}" loading="lazy">
        </div>`;
    }
  });

  // Interactive Plotly charts
  if (AVAILABLE_CHARTS.includes("interactive_scatter")) {
    html += `
      <div class="chart-card">
        <h4>🔵 Interactive Scatter (Plotly)</h4>
        <div class="plotly-wrap" id="plotlyScatter" style="min-height:350px"></div>
      </div>`;
  }
  if (AVAILABLE_CHARTS.includes("interactive_distribution")) {
    html += `
      <div class="chart-card" style="grid-column:span 2">
        <h4>📊 Interactive Distributions (Plotly)</h4>
        <div class="plotly-wrap" id="plotlyDist" style="min-height:450px"></div>
      </div>`;
  }

  html += "</div>";
  document.getElementById("edaContent").innerHTML = html;

  // Load Plotly charts
  if (AVAILABLE_CHARTS.includes("interactive_scatter")) loadPlotlyChart("plotlyScatter", "interactive_scatter");
  if (AVAILABLE_CHARTS.includes("interactive_distribution")) loadPlotlyChart("plotlyDist", "interactive_distribution");
}

async function loadPlotlyChart(containerId, chartName) {
  try {
    const res = await fetch(`/api/charts/image/${SESSION_ID}/${chartName}`);
    const data = await res.json();
    Plotly.newPlot(containerId, data.data, data.layout, { responsive: true, displayModeBar: true });
  } catch (e) { console.error("Plotly chart failed:", e); }
}

// ─── STATISTICS ─────────────────────────────────────────────────────
function renderStats() {
  const numStats = ANALYSIS_DATA.numeric_stats || {};
  const catStats = ANALYSIS_DATA.categorical_stats || {};

  let html = "";

  // Numeric stats
  if (Object.keys(numStats).length > 0) {
    html += `<div class="card"><div class="card-title"><span class="icon">📈</span>Numeric Column Statistics</div>`;
    html += `<div class="table-wrap"><table>
      <thead><tr>
        <th>Column</th><th>Count</th><th>Mean</th><th>Median</th><th>Std</th>
        <th>Min</th><th>Max</th><th>Skewness</th><th>Outliers</th><th>Normal?</th>
      </tr></thead><tbody>`;

    Object.entries(numStats).forEach(([col, s]) => {
      const skewTag = Math.abs(s.skewness) > 2 ? "tag-danger" : Math.abs(s.skewness) > 1 ? "tag-warn" : "tag-success";
      html += `<tr>
        <td><strong class="c-accent">${col}</strong></td>
        <td class="mono">${s.count?.toLocaleString()}</td>
        <td class="mono">${s.mean}</td>
        <td class="mono">${s.median}</td>
        <td class="mono">${s.std}</td>
        <td class="mono">${s.min}</td>
        <td class="mono">${s.max}</td>
        <td><span class="tag ${skewTag}">${s.skewness}</span></td>
        <td><span class="tag ${s.outliers?.count>0?'tag-warn':'tag-success'}">${s.outliers?.count||0}</span></td>
        <td>${s.normality?.is_normal ? '<span class="tag tag-success">✓ Yes</span>' : '<span class="tag tag-warn">✗ No</span>'}</td>
      </tr>`;
    });

    html += `</tbody></table></div></div>`;

    // Detailed per-column
    Object.entries(numStats).forEach(([col, s]) => {
      html += `
        <div class="card">
          <div class="card-title"><span class="icon">📊</span>${col} — Detailed Profile</div>
          <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px">
            <div>
              <div style="font-size:11px;color:var(--muted);font-weight:700;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.5px">Descriptive Statistics</div>
              ${[["Mean", s.mean,"c-accent"], ["Median", s.median,"c-green"], ["Std Dev", s.std,"c-purple"], ["Variance", s.variance,"c-muted"], ["Range", s.range,"c-orange"]].map(([k,v,c])=>`
                <div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--border);font-size:12px">
                  <span style="color:var(--muted)">${k}</span>
                  <span class="${c} mono">${v}</span>
                </div>`).join("")}
            </div>
            <div>
              <div style="font-size:11px;color:var(--muted);font-weight:700;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.5px">Percentiles</div>
              ${[["P1", s.percentiles?.p1], ["P5", s.percentiles?.p5], ["P25 (Q1)", s.percentiles?.p25], ["P50 (Median)", s.percentiles?.p50], ["P75 (Q3)", s.percentiles?.p75], ["P95", s.percentiles?.p95], ["P99", s.percentiles?.p99]].map(([k,v])=>`
                <div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid var(--border);font-size:12px">
                  <span style="color:var(--muted)">${k}</span>
                  <span class="mono">${v}</span>
                </div>`).join("")}
            </div>
            <div>
              <div style="font-size:11px;color:var(--muted);font-weight:700;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.5px">Distribution Shape</div>
              <div style="display:flex;flex-direction:column;gap:8px;font-size:12px">
                <div>Skewness: <span class="tag ${Math.abs(s.skewness)>2?'tag-danger':Math.abs(s.skewness)>1?'tag-warn':'tag-success'}">${s.skewness} (${s.distribution?.skew_direction})</span></div>
                <div>Kurtosis: <span class="mono">${s.kurtosis}</span></div>
                <div>CV: <span class="mono">${s.cv}%</span></div>
                <div>Normality: <span class="tag ${s.normality?.is_normal?'tag-success':'tag-warn'}">${s.normality?.test}: p=${s.normality?.p_value}</span></div>
                <div>Outliers: <span class="tag ${s.outliers?.count>0?'tag-warn':'tag-success'}">${s.outliers?.count} (${s.outliers?.percentage}%)</span></div>
              </div>
            </div>
          </div>
        </div>`;
    });
  }

  // Categorical stats
  if (Object.keys(catStats).length > 0) {
    html += `<div class="card"><div class="card-title"><span class="icon">🏷</span>Categorical Column Statistics</div>`;
    Object.entries(catStats).forEach(([col, s]) => {
      const top5 = Object.entries(s.value_counts||{}).slice(0,5);
      html += `
        <div style="margin-bottom:20px;padding-bottom:20px;border-bottom:1px solid var(--border)">
          <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px">
            <strong class="c-accent">${col}</strong>
            <span class="tag tag-info">unique: ${s.unique_values}</span>
            <span class="tag ${s.missing>0?'tag-warn':'tag-success'}">missing: ${s.missing_pct}%</span>
            ${s.is_binary ? '<span class="tag tag-purple">binary</span>' : ''}
            ${s.is_high_cardinality ? '<span class="tag tag-orange">high cardinality</span>' : ''}
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
            ${top5.map(([v,c])=>{
              const pct = s.value_percentages?.[v]||0;
              return `<div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:10px">
                <div style="display:flex;justify-content:space-between;margin-bottom:6px;font-size:12px">
                  <span style="font-weight:600">${v}</span>
                  <span class="c-accent">${c.toLocaleString()} (${pct}%)</span>
                </div>
                <div class="fill-bar"><div class="fill-bar-inner" style="width:${pct}%"></div></div>
              </div>`;
            }).join("")}
          </div>
          <div style="font-size:11px;color:var(--muted);margin-top:8px">Entropy: ${s.entropy}</div>
        </div>`;
    });
    html += "</div>";
  }

  // PCA Summary
  const pca = ANALYSIS_DATA.pca_summary;
  if (pca?.available) {
    html += `
      <div class="card">
        <div class="card-title"><span class="icon">🔬</span>PCA Summary</div>
        <div style="font-size:13px;color:var(--muted);margin-bottom:12px">Components needed for 90% variance: <strong class="c-accent">${pca.components_for_90pct}</strong></div>
        <div style="display:flex;gap:10px;flex-wrap:wrap">
          ${pca.explained_variance_ratio.map((v,i)=>`
            <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:12px;min-width:80px;text-align:center">
              <div style="font-size:10px;color:var(--muted);margin-bottom:4px">PC${i+1}</div>
              <div class="c-accent" style="font-size:18px;font-weight:800">${(v*100).toFixed(1)}%</div>
              <div style="font-size:10px;color:var(--dim)">cumul: ${(pca.cumulative_variance[i]*100).toFixed(1)}%</div>
            </div>`).join("")}
        </div>
      </div>`;
  }

  document.getElementById("statsContent").innerHTML = html;
}

// ─── DATA QUALITY ───────────────────────────────────────────────────
function renderQuality() {
  const qr = ANALYSIS_DATA.quality_report || {};
  const score = qr.quality_score || 0;
  const scoreColor = score >= 80 ? "var(--green)" : score >= 60 ? "var(--orange)" : "var(--red)";
  const issues = qr.issues || [];
  const recs = qr.recommendations || [];

  const sevIcons = { critical: "🔴", warning: "⚠️", info: "ℹ️" };
  const sevDotColors = { critical: "var(--red)", warning: "var(--orange)", info: "var(--accent)" };

  document.getElementById("qualityContent").innerHTML = `
    <div class="card" style="text-align:center">
      <div style="font-size:64px;font-weight:800;color:${scoreColor}">${score}</div>
      <div style="font-size:14px;color:var(--muted);margin-bottom:16px">Data Quality Score / 100</div>
      <div style="display:flex;justify-content:center;gap:16px">
        <span class="tag tag-danger">🔴 Critical: ${qr.summary?.critical||0}</span>
        <span class="tag tag-warn">⚠️ Warnings: ${qr.summary?.warning||0}</span>
        <span class="tag tag-info">ℹ️ Info: ${qr.summary?.info||0}</span>
      </div>
    </div>

    <div class="card">
      <div class="card-title"><span class="icon">🔍</span>Issues Found (${issues.length})</div>
      ${issues.length === 0
        ? '<div style="color:var(--green);text-align:center;padding:20px">✅ No issues found! Your data is clean.</div>'
        : issues.map(i => `
          <div class="issue-item">
            <div class="issue-dot" style="background:${sevDotColors[i.severity]}"></div>
            <div>
              <div style="font-size:11px;color:var(--muted);margin-bottom:2px;text-transform:uppercase;letter-spacing:0.5px">${i.severity} — ${i.type} — ${i.column}</div>
              ${sevIcons[i.severity]} ${i.message}
            </div>
          </div>`).join("")}
    </div>

    ${recs.length > 0 ? `
    <div class="card">
      <div class="card-title"><span class="icon">💡</span>Recommendations</div>
      ${recs.map(r => `
        <div style="display:flex;gap:10px;padding:10px;background:var(--surface);border:1px solid var(--border);border-radius:8px;margin-bottom:8px;font-size:13px">
          <span style="color:var(--accent)">→</span>${r}
        </div>`).join("")}
    </div>` : ""}
  `;
}

// ─── CORRELATION ────────────────────────────────────────────────────
function renderCorrelation() {
  const corr = ANALYSIS_DATA.correlations || {};
  const pearson = corr.pearson || {};
  const strong = corr.strong_pairs || [];
  const cols = Object.keys(pearson);

  if (cols.length < 2) {
    document.getElementById("correlationContent").innerHTML =
      '<div class="card"><div style="color:var(--muted);text-align:center;padding:40px">Need at least 2 numeric columns for correlation analysis.</div></div>';
    return;
  }

  const cellClass = v => Math.abs(v) > 0.7 ? "cv-high" : Math.abs(v) > 0.4 ? "cv-mid" : v < -0.4 ? "cv-neg" : "cv-low";

  document.getElementById("correlationContent").innerHTML = `
    ${strong.length > 0 ? `
    <div class="card">
      <div class="card-title"><span class="icon">💪</span>Strong Correlations (|r| ≥ 0.5)</div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Column 1</th><th>Column 2</th><th>Pearson r</th><th>Strength</th><th>Direction</th></tr></thead>
          <tbody>
            ${strong.map(p => `
              <tr>
                <td class="mono c-accent">${p.col1}</td>
                <td class="mono c-purple">${p.col2}</td>
                <td class="mono"><strong style="color:${Math.abs(p.pearson_r)>0.7?'var(--green)':'var(--orange)'}">${p.pearson_r}</strong></td>
                <td><span class="tag ${Math.abs(p.pearson_r)>0.9?'tag-success':Math.abs(p.pearson_r)>0.7?'tag-info':'tag-warn'}">${p.strength}</span></td>
                <td><span class="tag ${p.direction==='positive'?'tag-success':'tag-danger'}">${p.direction}</span></td>
              </tr>`).join("")}
          </tbody>
        </table>
      </div>
    </div>` : ""}

    <div class="card">
      <div class="card-title"><span class="icon">🔗</span>Pearson Correlation Matrix</div>
      <div style="font-size:11px;color:var(--muted);margin-bottom:12px">
        <span class="tag tag-success">Strong (>0.7)</span>
        <span class="tag tag-warn" style="margin-left:6px">Moderate (0.4-0.7)</span>
        <span class="tag tag-danger" style="margin-left:6px">Negative (<-0.4)</span>
      </div>
      <div class="table-wrap">
        <table class="corr-table">
          <thead><tr><th></th>${cols.map(c=>`<th title="${c}">${c.length>8?c.substring(0,8)+"..":c}</th>`).join("")}</tr></thead>
          <tbody>
            ${cols.map((c1,i) => `
              <tr>
                <th style="text-align:left;font-size:11px;padding:8px">${c1.length>10?c1.substring(0,10)+"..":c1}</th>
                ${cols.map((c2,j) => {
                  const v = pearson[c1]?.[c2];
                  if (i === j) return `<td>—</td>`;
                  return `<td class="corr-val ${cellClass(v)}">${typeof v==='number'?v.toFixed(2):'—'}</td>`;
                }).join("")}
              </tr>`).join("")}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

// ─── TRANSFORM PANEL ───────────────────────────────────────────────
function renderTransform() {
  const cols = Object.keys(ANALYSIS_DATA.overview?.dtypes || {});
  const numCols = ANALYSIS_DATA.overview?.column_types?.numeric || [];
  const catCols = ANALYSIS_DATA.overview?.column_types?.categorical || [];

  const colOptions = cols.map(c => `<option value="${c}">${c}</option>`).join("");
  const numOptions = numCols.map(c => `<option value="${c}">${c}</option>`).join("");

  document.getElementById("transformContent").innerHTML = `
    <div class="transform-grid">

      <!-- Drop Duplicates -->
      <div class="transform-card">
        <h4>🗑 Drop Duplicates</h4>
        <p style="color:var(--muted);font-size:12px;margin-bottom:12px">Remove all duplicate rows from dataset</p>
        <button class="btn-sm" onclick="runTransform('drop_duplicates', {}, 'res_dup')">Remove Duplicates</button>
        <div class="transform-result" id="res_dup"></div>
      </div>

      <!-- Drop Column -->
      <div class="transform-card">
        <h4>❌ Drop Column</h4>
        <div class="form-group">
          <label>Column to Drop</label>
          <select id="t_drop_col">${colOptions}</select>
        </div>
        <button class="btn-sm" onclick="runTransform('drop_column', {column: document.getElementById('t_drop_col').value}, 'res_dc')">Drop Column</button>
        <div class="transform-result" id="res_dc"></div>
      </div>

      <!-- Fill Missing -->
      <div class="transform-card">
        <h4>🔧 Fill Missing Values</h4>
        <div class="form-group">
          <label>Column</label>
          <select id="t_fill_col">${colOptions}</select>
        </div>
        <div class="form-group">
          <label>Method</label>
          <select id="t_fill_method">
            <option value="mean">Mean (numeric)</option>
            <option value="median">Median (numeric)</option>
            <option value="mode">Mode (any)</option>
            <option value="zero">Zero / Empty string</option>
            <option value="forward">Forward Fill</option>
            <option value="backward">Backward Fill</option>
          </select>
        </div>
        <button class="btn-sm" onclick="runTransform('fill_missing', {column: document.getElementById('t_fill_col').value, method: document.getElementById('t_fill_method').value}, 'res_fm')">Fill Missing</button>
        <div class="transform-result" id="res_fm"></div>
      </div>

      <!-- Normalize -->
      <div class="transform-card">
        <h4>📐 Normalize Column</h4>
        <div class="form-group">
          <label>Numeric Column</label>
          <select id="t_norm_col">${numOptions}</select>
        </div>
        <div class="form-group">
          <label>Method</label>
          <select id="t_norm_method">
            <option value="minmax">Min-Max Scaling (0 to 1)</option>
            <option value="zscore">Z-Score Standardization</option>
            <option value="log">Log Transformation (log1p)</option>
          </select>
        </div>
        <button class="btn-sm" onclick="runTransform('normalize', {column: document.getElementById('t_norm_col').value, method: document.getElementById('t_norm_method').value}, 'res_norm')">Normalize</button>
        <div class="transform-result" id="res_norm"></div>
      </div>

      <!-- Create Column -->
      <div class="transform-card">
        <h4>✨ Create New Column</h4>
        <div class="form-group">
          <label>New Column Name</label>
          <input type="text" id="t_new_name" placeholder="e.g. profit_margin">
        </div>
        <div class="form-group">
          <label>Expression (use column names)</label>
          <input type="text" id="t_expression" placeholder="e.g. salary * 0.1  OR  age + experience">
        </div>
        <button class="btn-sm" onclick="runTransform('create_column', {name: document.getElementById('t_new_name').value, expression: document.getElementById('t_expression').value}, 'res_cc')">Create Column</button>
        <div class="transform-result" id="res_cc"></div>
      </div>

      <!-- Sort -->
      <div class="transform-card">
        <h4>↕ Sort Dataset</h4>
        <div class="form-group">
          <label>Sort by Column</label>
          <select id="t_sort_col">${colOptions}</select>
        </div>
        <div class="form-group">
          <label>Order</label>
          <select id="t_sort_order">
            <option value="true">Ascending (A→Z / 0→9)</option>
            <option value="false">Descending (Z→A / 9→0)</option>
          </select>
        </div>
        <button class="btn-sm" onclick="runTransform('sort', {column: document.getElementById('t_sort_col').value, ascending: document.getElementById('t_sort_order').value === 'true'}, 'res_sort')">Sort</button>
        <div class="transform-result" id="res_sort"></div>
      </div>

      <!-- Filter Rows -->
      <div class="transform-card">
        <h4>🔎 Filter Rows</h4>
        <div class="form-group">
          <label>Query Expression</label>
          <input type="text" id="t_filter" placeholder="e.g. age > 25 and salary > 50000">
        </div>
        <div style="font-size:11px;color:var(--muted);margin-bottom:10px">Uses pandas .query() syntax</div>
        <button class="btn-sm" onclick="runTransform('filter_rows', {expression: document.getElementById('t_filter').value}, 'res_filter')">Apply Filter</button>
        <div class="transform-result" id="res_filter"></div>
      </div>

    </div>
  `;
}

async function runTransform(operation, params, resultId) {
  const resEl = document.getElementById(resultId);
  resEl.style.display = "block";
  resEl.className = "transform-result";
  resEl.textContent = "Running...";

  try {
    const res = await fetch(`/api/analysis/transform/${SESSION_ID}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ operation, params })
    });
    const data = await res.json();
    if (data.success) {
      resEl.className = "transform-result success";
      resEl.textContent = `✅ Done! ${data.original_shape[0]}×${data.original_shape[1]} → ${data.new_shape[0]}×${data.new_shape[1]}`;
      // Refresh analysis
      const analysis = await fetchAnalysis();
      if (analysis) {
        ANALYSIS_DATA = analysis;
        renderOverview(); renderStats(); renderQuality(); renderCorrelation();
        renderTransform(); // re-render with new columns
      }
    } else {
      resEl.className = "transform-result error";
      resEl.textContent = "❌ " + data.error;
    }
  } catch (e) {
    resEl.className = "transform-result error";
    resEl.textContent = "❌ Network error: " + e.message;
  }
}

// ─── PREVIEW ────────────────────────────────────────────────────────
async function renderPreview() {
  try {
    const res = await fetch(`/api/analysis/preview/${SESSION_ID}?n=100`);
    const data = await res.json();
    const cols = data.columns || [];
    const rows = data.data || [];

    document.getElementById("previewContent").innerHTML = `
      <div class="card" style="margin-bottom:12px;display:flex;justify-content:space-between;align-items:center;padding:12px 16px">
        <span style="color:var(--muted);font-size:13px">Showing first 100 of <strong class="c-accent">${data.total_rows?.toLocaleString()}</strong> rows</span>
        <div style="display:flex;gap:8px">
          <button class="btn-sm secondary" style="width:auto;padding:6px 14px" onclick="downloadCSV()">⬇ CSV</button>
          <button class="btn-sm secondary" style="width:auto;padding:6px 14px" onclick="downloadExcel()">📊 Excel</button>
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr>#${cols.map(c=>`<th title="${data.dtypes?.[c]||''}">${c}<br><span style="color:var(--accent);font-size:9px">${data.dtypes?.[c]||''}</span></th>`).join("")}</tr></thead>
          <tbody>
            ${rows.map((row,i)=>`<tr><td class="mono" style="color:var(--dim)">${i+1}</td>${cols.map(c=>`<td class="mono">${row[c]===''||row[c]==null?'<span style="color:var(--dim);font-size:10px">null</span>':row[c]}</td>`).join("")}</tr>`).join("")}
          </tbody>
        </table>
      </div>`;
  } catch (e) {
    document.getElementById("previewContent").innerHTML = `<div class="card"><p style="color:var(--red)">Error loading preview: ${e.message}</p></div>`;
  }
}

// ─── TAB SWITCH ─────────────────────────────────────────────────────
function switchTab(tab) {
  document.querySelectorAll(".nav-item").forEach(el => {
    el.classList.toggle("active", el.dataset.tab === tab);
  });
  document.querySelectorAll(".tab-panel").forEach(el => {
    el.classList.toggle("active", el.id === `panel-${tab}`);
  });
}

// ─── DOWNLOADS ──────────────────────────────────────────────────────
function downloadCSV() {
  if (!SESSION_ID) return;
  window.location.href = `/api/analysis/download/csv/${SESSION_ID}`;
}
function downloadExcel() {
  if (!SESSION_ID) return;
  window.location.href = `/api/analysis/download/excel/${SESSION_ID}`;
}
function downloadReport() {
  if (!SESSION_ID) return;
  addChatMsg("ai", "📄 Generating PDF report... please wait.");
  window.location.href = `/api/report/pdf/${SESSION_ID}`;
}

// ─── CHAT ────────────────────────────────────────────────────────────
async function sendChat() {
  const input = document.getElementById("chatInput");
  const msg = input.value.trim();
  if (!msg) return;
  input.value = "";

  addChatMsg("user", msg);
  showTyping();

  if (!SESSION_ID) {
    hideTyping();
    addChatMsg("ai", "⚠️ Pehle koi dataset load karo bhai!");
    return;
  }

  try {
    const res = await fetch(`/api/chat/message/${SESSION_ID}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg, history: CHAT_HISTORY.slice(-8) })
    });
    const data = await res.json();
    hideTyping();

    const reply = data.reply || "Sorry, kuch error aayi.";
    addChatMsg("ai", formatMsg(reply));
    CHAT_HISTORY.push({ role: "user", content: msg });
    CHAT_HISTORY.push({ role: "assistant", content: reply });

    // If transform was applied, refresh views
    if (data.transform_result?.success) {
      addChatMsg("ai", `✅ Transform applied! Shape: ${data.transform_result.new_shape[0]} × ${data.transform_result.new_shape[1]}`);
      const analysis = await fetchAnalysis();
      if (analysis) { ANALYSIS_DATA = analysis; renderAll(); }
    }
  } catch (e) {
    hideTyping();
    addChatMsg("ai", `❌ API error. Make sure ANTHROPIC_API_KEY is set in .env file.<br><small style="color:var(--muted)">${e.message}</small>`);
  }
}

function sendQuick(q) {
  document.getElementById("chatInput").value = q;
  sendChat();
}

function formatMsg(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>")
    .replace(/```([\s\S]*?)```/g, "<pre>$1</pre>")
    .replace(/^- (.+)$/gm, "<li>$1</li>")
    .replace(/(<li>.*<\/li>)/gs, "<ul>$1</ul>")
    .replace(/\n/g, "<br>");
}

let typingEl = null;
function showTyping() {
  const msgs = document.getElementById("chatMsgs");
  typingEl = document.createElement("div");
  typingEl.className = "chat-msg ai-msg";
  typingEl.id = "typingMsg";
  typingEl.innerHTML = `<div class="msg-text"><div class="typing-dots"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div></div>`;
  msgs.appendChild(typingEl);
  msgs.scrollTop = msgs.scrollHeight;
}
function hideTyping() {
  document.getElementById("typingMsg")?.remove();
}

function addChatMsg(role, text) {
  const msgs = document.getElementById("chatMsgs");
  const div = document.createElement("div");
  div.className = `chat-msg ${role === "ai" ? "ai-msg" : "user-msg"}`;
  div.innerHTML = `<div class="msg-text">${text}</div>`;
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
}

// ─── RESET ──────────────────────────────────────────────────────────
function resetApp() {
  SESSION_ID = null; ANALYSIS_DATA = null; AVAILABLE_CHARTS = []; CHAT_HISTORY = [];
  document.getElementById("analysisScreen").style.display = "none";
  document.getElementById("uploadScreen").style.display = "block";
  document.getElementById("datasetBadge").style.display = "none";
  document.getElementById("resetBtn").style.display = "none";
  document.getElementById("pasteArea").value = "";
  document.getElementById("fileInput").value = "";
  document.getElementById("chatMsgs").innerHTML = `
    <div class="chat-msg ai-msg">
      <div class="msg-text">👋 <strong>Reset ho gaya!</strong> Naya dataset load karo. 🚀</div>
    </div>`;
}
