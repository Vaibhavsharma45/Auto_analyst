"""
backend/routes/extras_routes.py
DB Connect, Email Report, PPT Download, NL-to-Chart
"""
import os, uuid
from flask import Blueprint, request, jsonify, send_file, current_app
from backend.utils.session_store import get_session, get_df, save_session, update_session
from backend.utils.db_connector import test_connection, get_tables, load_table, run_query
from backend.utils.email_sender import send_report_email
from backend.analysis.eda_engine import EDAEngine
from backend.analysis.chart_generator import ChartGenerator

extras_bp = Blueprint("extras", __name__)


# ── DATABASE ───────────────────────────────────────────────────────
@extras_bp.route("/db/test", methods=["POST"])
def db_test():
    body = request.get_json() or {}
    return jsonify(test_connection(body.get("db_type", "sqlite"), body.get("config", {})))

@extras_bp.route("/db/tables", methods=["POST"])
def db_tables():
    body = request.get_json() or {}
    return jsonify(get_tables(body.get("db_type", "sqlite"), body.get("config", {})))

@extras_bp.route("/db/load", methods=["POST"])
def db_load():
    body = request.get_json() or {}
    db_type = body.get("db_type", "sqlite")
    config = body.get("config", {})
    table = body.get("table", "")
    custom_query = body.get("query", "")
    try:
        if custom_query:
            df = run_query(db_type, config, custom_query)
        else:
            df = load_table(db_type, config, table)
        session_id = str(uuid.uuid4())
        save_session(session_id, df, filename=f"{table or 'query'}.db")
        from backend.utils.data_loader import get_sample_info
        return jsonify({"session_id": session_id, "info": get_sample_info(df), "filename": f"{table}.db"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── EMAIL ─────────────────────────────────────────────────────────
@extras_bp.route("/email/<session_id>", methods=["POST"])
def email_report(session_id):
    session = get_session(session_id)
    if not session: return jsonify({"error": "Session not found"}), 404

    body = request.get_json() or {}
    to_email = body.get("email", "")
    if not to_email: return jsonify({"error": "Email address required"}), 400

    df = session["df"]
    analysis = session.get("analysis") or EDAEngine(df).run_full_analysis()
    charts = session.get("charts") or ChartGenerator(df).generate_all()

    # Generate PDF first
    from backend.analysis.report_generator import ReportGenerator
    import tempfile
    pdf_path = os.path.join(tempfile.gettempdir(), f"report_{uuid.uuid4().hex[:8]}.pdf")
    try:
        gen = ReportGenerator(df, analysis, charts, session.get("filename", "dataset"))
        gen.generate_pdf(pdf_path)
    except Exception as e:
        return jsonify({"error": f"PDF generation failed: {str(e)}"}), 500

    # Send email
    summary = f"Quality Score: {analysis.get('quality_report',{}).get('quality_score',0)}/100"
    result = send_report_email(to_email, pdf_path, session.get("filename","dataset"), summary)
    # Cleanup temp PDF
    try:
        if os.path.exists(pdf_path): os.remove(pdf_path)
    except: pass
    return jsonify(result)


# ── POWERPOINT ────────────────────────────────────────────────────
@extras_bp.route("/ppt/<session_id>", methods=["GET"])
def download_ppt(session_id):
    session = get_session(session_id)
    if not session: return jsonify({"error": "Session not found"}), 404

    df = session["df"]
    analysis = session.get("analysis") or EDAEngine(df).run_full_analysis()
    charts = session.get("charts") or ChartGenerator(df).generate_all()
    goal = session.get("goal", {})

    output_path = os.path.join(current_app.config["REPORTS_FOLDER"], f"ppt_{uuid.uuid4().hex[:8]}.pptx")
    try:
        from backend.analysis.ppt_generator import PPTGenerator
        gen = PPTGenerator(df, analysis, charts, goal, session.get("filename","dataset"))
        result_path = gen.generate(output_path)
        return send_file(result_path, mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                         as_attachment=True, download_name="datamind-analysis.pptx")
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── NL TO CHART ───────────────────────────────────────────────────
@extras_bp.route("/nl-chart/<session_id>", methods=["POST"])
def nl_to_chart(session_id):
    """Natural language to chart — 'bar chart banao sales ka' """
    session = get_session(session_id)
    if not session: return jsonify({"error": "Session not found"}), 404

    body = request.get_json() or {}
    user_request = body.get("request", "")
    if not user_request: return jsonify({"error": "Request required"}), 400

    df = session["df"]
    cols = df.columns.tolist()
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include="object").columns.tolist()

    # Parse request with AI
    import os, json
    groq_key = os.getenv("GROQ_API_KEY", "")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")

    parse_prompt = f"""User wants a chart: "{user_request}"

Available columns: {cols}
Numeric columns: {num_cols}
Categorical columns: {cat_cols}

Return ONLY this JSON:
{{"chart_type": "bar|line|scatter|pie|histogram|box", "x_col": "column_name_or_null", "y_col": "column_name_or_null", "title": "Chart title", "color_col": "column_name_or_null"}}

chart_type must be one of: bar, line, scatter, pie, histogram, box
Match column names EXACTLY from the available list above."""

    chart_spec = None
    try:
        if groq_key:
            import requests as req
            r = req.post("https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
                json={"model": "llama-3.3-70b-versatile",
                      "messages": [{"role": "user", "content": parse_prompt}],
                      "max_tokens": 200, "temperature": 0.1},
                timeout=15)
            text = r.json()["choices"][0]["message"]["content"].strip()
            text = text.replace("```json","").replace("```","").strip()
            chart_spec = json.loads(text)
        elif anthropic_key:
            import anthropic
            client = anthropic.Anthropic(api_key=anthropic_key)
            resp = client.messages.create(model="claude-sonnet-4-20250514", max_tokens=200,
                messages=[{"role":"user","content":parse_prompt}])
            text = resp.content[0].text.strip().replace("```json","").replace("```","").strip()
            chart_spec = json.loads(text)
    except Exception as e:
        chart_spec = _fallback_parse(user_request, num_cols, cat_cols)

    if not chart_spec:
        chart_spec = _fallback_parse(user_request, num_cols, cat_cols)

    # Generate the chart
    try:
        chart_image = _generate_nl_chart(df, chart_spec)
        return jsonify({"success": True, "chart": chart_image, "spec": chart_spec})
    except Exception as e:
        return jsonify({"error": f"Chart generation failed: {str(e)}", "spec": chart_spec}), 500


def _fallback_parse(request_text: str, num_cols: list, cat_cols: list) -> dict:
    """Rule-based fallback parser"""
    text = request_text.lower()
    chart_type = "bar"
    if "line" in text or "trend" in text or "over time" in text: chart_type = "line"
    elif "scatter" in text or "vs" in text: chart_type = "scatter"
    elif "pie" in text or "distribution" in text: chart_type = "pie"
    elif "histogram" in text or "hist" in text: chart_type = "histogram"
    elif "box" in text or "outlier" in text: chart_type = "box"

    x_col = cat_cols[0] if cat_cols else (num_cols[0] if num_cols else None)
    y_col = num_cols[0] if num_cols else None

    # Try to match column names in request
    all_cols = num_cols + cat_cols
    for col in all_cols:
        if col.lower() in text:
            if col in num_cols:
                y_col = col
            else:
                x_col = col

    return {"chart_type": chart_type, "x_col": x_col, "y_col": y_col,
            "title": f"{chart_type.title()} Chart", "color_col": None}


def _generate_nl_chart(df, spec: dict) -> str:
    """Generate chart from spec and return base64 image"""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import io, base64

    chart_type = spec.get("chart_type", "bar")
    x_col = spec.get("x_col")
    y_col = spec.get("y_col")
    title = spec.get("title", "Chart")
    color_col = spec.get("color_col")

    DARK_BG = "#0d1117"
    CARD_BG = "#161b22"
    ACCENT = "#58a6ff"
    TEXT = "#e6edf3"
    MUTED = "#8b949e"
    GRID = "#21262d"

    plt.rcParams.update({"figure.facecolor": DARK_BG, "axes.facecolor": CARD_BG,
                         "axes.edgecolor": GRID, "text.color": TEXT, "axes.labelcolor": TEXT,
                         "xtick.color": MUTED, "ytick.color": MUTED, "grid.color": GRID,
                         "axes.grid": True, "grid.linewidth": 0.5})

    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor(DARK_BG)

    PALETTE = ["#58a6ff","#bc8cff","#3fb950","#d29922","#f85149","#79c0ff"]

    try:
        if chart_type == "bar" and x_col and y_col and x_col in df and y_col in df:
            data = df.groupby(x_col)[y_col].sum().sort_values(ascending=False).head(12)
            colors = [PALETTE[i % len(PALETTE)] for i in range(len(data))]
            ax.bar(data.index.astype(str), data.values, color=colors, edgecolor="none")
            ax.set_xlabel(x_col); ax.set_ylabel(y_col)
            plt.xticks(rotation=30, ha="right")

        elif chart_type == "line" and y_col and y_col in df:
            vals = df[y_col].dropna().values[:50]
            ax.plot(range(len(vals)), vals, color=ACCENT, linewidth=2.5)
            ax.fill_between(range(len(vals)), vals, alpha=0.15, color=ACCENT)
            ax.set_ylabel(y_col)

        elif chart_type == "scatter" and x_col and y_col and x_col in df and y_col in df:
            ax.scatter(df[x_col], df[y_col], color=ACCENT, alpha=0.5, s=30)
            ax.set_xlabel(x_col); ax.set_ylabel(y_col)

        elif chart_type == "pie" and x_col and x_col in df:
            vc = df[x_col].value_counts().head(7)
            ax.pie(vc.values, labels=vc.index, colors=PALETTE[:len(vc)],
                   autopct="%1.1f%%", pctdistance=0.75,
                   wedgeprops={"edgecolor": DARK_BG, "linewidth": 2})

        elif chart_type == "histogram" and y_col and y_col in df:
            ax.hist(df[y_col].dropna(), bins=25, color=ACCENT, alpha=0.7, edgecolor="none")
            ax.set_xlabel(y_col)

        elif chart_type == "box" and y_col and y_col in df:
            data = df[y_col].dropna()
            bp = ax.boxplot([data], patch_artist=True,
                            medianprops={"color":"#3fb950","linewidth":2.5},
                            whiskerprops={"color": MUTED},
                            capprops={"color": MUTED},
                            flierprops={"marker":"o","markersize":3,"alpha":0.4})
            bp["boxes"][0].set(facecolor=ACCENT+"44", edgecolor=ACCENT)
            ax.set_xticks([1]); ax.set_xticklabels([y_col])
        else:
            ax.text(0.5, 0.5, "Chart could not be generated\nCheck column names", ha="center", va="center",
                    fontsize=14, color=MUTED, transform=ax.transAxes)
    except Exception as e:
        ax.text(0.5, 0.5, f"Error: {str(e)}", ha="center", va="center",
                fontsize=12, color="#f85149", transform=ax.transAxes)

    ax.set_title(title, fontsize=14, fontweight="bold", color=TEXT, pad=12)
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight", facecolor=DARK_BG)
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return f"data:image/png;base64,{img_b64}"