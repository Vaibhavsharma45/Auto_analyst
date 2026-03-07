"""
backend/routes/analysis_routes.py
"""
from flask import Blueprint, request, jsonify
from backend.utils.session_store import get_session, get_df, apply_df_operation, update_session
from backend.analysis.eda_engine import EDAEngine

analysis_bp = Blueprint("analysis", __name__)

@analysis_bp.route("/full/<session_id>", methods=["GET"])
def full_analysis(session_id):
    df = get_df(session_id)
    if df is None:
        return jsonify({"error": "Session not found or expired"}), 404
    try:
        engine = EDAEngine(df)
        result = engine.run_full_analysis()
        update_session(session_id, analysis=result)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analysis_bp.route("/overview/<session_id>")
def overview(session_id):
    df = get_df(session_id)
    if df is None:
        return jsonify({"error": "Session not found"}), 404
    return jsonify(EDAEngine(df).get_overview())

@analysis_bp.route("/numeric/<session_id>")
def numeric(session_id):
    df = get_df(session_id)
    if df is None:
        return jsonify({"error": "Session not found"}), 404
    return jsonify(EDAEngine(df).get_numeric_stats())

@analysis_bp.route("/categorical/<session_id>")
def categorical(session_id):
    df = get_df(session_id)
    if df is None:
        return jsonify({"error": "Session not found"}), 404
    return jsonify(EDAEngine(df).get_categorical_stats())

@analysis_bp.route("/correlations/<session_id>")
def correlations(session_id):
    df = get_df(session_id)
    if df is None:
        return jsonify({"error": "Session not found"}), 404
    return jsonify(EDAEngine(df).get_correlations())

@analysis_bp.route("/quality/<session_id>")
def quality(session_id):
    df = get_df(session_id)
    if df is None:
        return jsonify({"error": "Session not found"}), 404
    return jsonify(EDAEngine(df).get_quality_report())

@analysis_bp.route("/preview/<session_id>")
def preview(session_id):
    df = get_df(session_id)
    if df is None:
        return jsonify({"error": "Session not found"}), 404
    n = int(request.args.get("n", 50))
    return jsonify({
        "columns": df.columns.tolist(),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "data": df.head(n).fillna("").to_dict("records"),
        "total_rows": len(df)
    })

@analysis_bp.route("/transform/<session_id>", methods=["POST"])
def transform(session_id):
    body = request.get_json()
    if not body:
        return jsonify({"error": "No body"}), 400
    result = apply_df_operation(session_id, body.get("operation"), body.get("params", {}))
    return jsonify(result)

@analysis_bp.route("/download/csv/<session_id>")
def download_csv(session_id):
    from flask import Response
    from backend.utils.data_loader import df_to_csv_string
    df = get_df(session_id)
    if df is None:
        return jsonify({"error": "Session not found"}), 404
    return Response(
        df_to_csv_string(df),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=datamind-export.csv"}
    )

@analysis_bp.route("/download/excel/<session_id>")
def download_excel(session_id):
    from flask import Response
    from backend.utils.data_loader import df_to_excel_bytes
    df = get_df(session_id)
    if df is None:
        return jsonify({"error": "Session not found"}), 404
    return Response(
        df_to_excel_bytes(df),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=datamind-export.xlsx"}
    )

