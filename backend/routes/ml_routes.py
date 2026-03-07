"""
backend/routes/ml_routes.py
ML Predictions, Forecasting, Clustering
"""
from flask import Blueprint, request, jsonify
from backend.utils.session_store import get_session, get_df
from backend.analysis.ml_engine import MLEngine

ml_bp = Blueprint("ml", __name__)

@ml_bp.route("/suggestions/<session_id>")
def suggestions(session_id):
    df = get_df(session_id)
    if df is None: return jsonify({"error": "Session not found"}), 404
    return jsonify(MLEngine(df).get_ml_suggestions())

@ml_bp.route("/regression/<session_id>", methods=["POST"])
def regression(session_id):
    df = get_df(session_id)
    if df is None: return jsonify({"error": "Session not found"}), 404
    body = request.get_json() or {}
    target = body.get("target")
    features = body.get("features")
    if not target: return jsonify({"error": "target column required"}), 400
    return jsonify(MLEngine(df).run_regression(target, features))

@ml_bp.route("/classification/<session_id>", methods=["POST"])
def classification(session_id):
    df = get_df(session_id)
    if df is None: return jsonify({"error": "Session not found"}), 404
    body = request.get_json() or {}
    target = body.get("target")
    features = body.get("features")
    if not target: return jsonify({"error": "target column required"}), 400
    return jsonify(MLEngine(df).run_classification(target, features))

@ml_bp.route("/clustering/<session_id>", methods=["POST"])
def clustering(session_id):
    df = get_df(session_id)
    if df is None: return jsonify({"error": "Session not found"}), 404
    body = request.get_json() or {}
    n = body.get("n_clusters")
    features = body.get("features")
    return jsonify(MLEngine(df).run_clustering(n, features))

@ml_bp.route("/forecasting/<session_id>", methods=["POST"])
def forecasting(session_id):
    df = get_df(session_id)
    if df is None: return jsonify({"error": "Session not found"}), 404
    body = request.get_json() or {}
    target = body.get("target")
    periods = int(body.get("periods", 6))
    if not target: return jsonify({"error": "target column required"}), 400
    return jsonify(MLEngine(df).run_forecasting(target, periods))
