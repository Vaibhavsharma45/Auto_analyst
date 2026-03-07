"""
backend/routes/chart_routes.py
"""
from flask import Blueprint, jsonify
from backend.utils.session_store import get_df, get_session, update_session
from backend.analysis.chart_generator import ChartGenerator

chart_bp = Blueprint("charts", __name__)

@chart_bp.route("/all/<session_id>", methods=["GET"])
def all_charts(session_id):
    df = get_df(session_id)
    if df is None:
        return jsonify({"error": "Session not found"}), 404
    try:
        gen = ChartGenerator(df)
        charts = gen.generate_all()
        update_session(session_id, charts=charts)
        # Don't return base64 images in JSON directly — return keys only
        available = {k: True for k in charts}
        return jsonify({"available_charts": list(available.keys()), "count": len(available)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chart_bp.route("/image/<session_id>/<chart_name>", methods=["GET"])
def get_chart(session_id, chart_name):
    from flask import Response
    import base64
    session = get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404
    charts = session.get("charts", {})
    if not charts:
        df = session["df"]
        gen = ChartGenerator(df)
        charts = gen.generate_all()
        update_session(session_id, charts=charts)
    chart = charts.get(chart_name)
    if chart is None:
        return jsonify({"error": f"Chart '{chart_name}' not found"}), 404
    if isinstance(chart, str) and chart.startswith("data:image/png;base64,"):
        img_data = base64.b64decode(chart.split(",")[1])
        return Response(img_data, mimetype="image/png")
    elif isinstance(chart, dict):
        return jsonify(chart)  # Plotly JSON
    return jsonify({"error": "Invalid chart format"}), 500

@chart_bp.route("/categorical/<session_id>/<int:index>", methods=["GET"])
def categorical_chart(session_id, index):
    from flask import Response
    import base64
    session = get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404
    charts = session.get("charts", {})
    cat_charts = charts.get("categorical_charts", [])
    if index >= len(cat_charts):
        return jsonify({"error": "Index out of range"}), 404
    val = cat_charts[index].get("image", "")
    if val.startswith("data:image/png;base64,"):
        img_data = base64.b64decode(val.split(",")[1])
        return Response(img_data, mimetype="image/png")
    return jsonify({"error": "No image"}), 500
