"""NLP Routes"""
from flask import Blueprint, jsonify, request
from backend.utils.session_store import get_session
from backend.analysis.nlp_engine import analyze_column, analyze_sentiment, get_keywords, text_statistics
import pandas as pd

nlp_bp = Blueprint('nlp', __name__)

@nlp_bp.route('/api/nlp/analyze/<session_id>', methods=['POST'])
def nlp_analyze(session_id):
    try:
        session = get_session(session_id)
        if not session: return jsonify({"error": "Session expired"}), 404
        df = session['dataframe']
        data = request.get_json() or {}
        col = data.get('column')
        if not col or col not in df.columns:
            # Auto-detect text columns
            text_cols = df.select_dtypes(include='object').columns.tolist()
            if not text_cols: return jsonify({"error": "No text columns found"}), 400
            col = text_cols[0]
        result = analyze_column(df[col])
        result['column'] = col
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@nlp_bp.route('/api/nlp/sentiment/<session_id>', methods=['POST'])
def nlp_sentiment(session_id):
    try:
        data = request.get_json() or {}
        text = data.get('text', '')
        if not text: return jsonify({"error": "No text provided"}), 400
        return jsonify(analyze_sentiment(text))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@nlp_bp.route('/api/nlp/keywords/<session_id>', methods=['POST'])
def nlp_keywords(session_id):
    try:
        session = get_session(session_id)
        if not session: return jsonify({"error": "Session expired"}), 404
        df = session['dataframe']
        data = request.get_json() or {}
        col = data.get('column')
        if not col or col not in df.columns:
            text_cols = df.select_dtypes(include='object').columns.tolist()
            if not text_cols: return jsonify({"error": "No text columns"}), 400
            col = text_cols[0]
        corpus = ' '.join(df[col].dropna().astype(str).tolist())
        keywords = get_keywords(corpus, 30)
        stats = text_statistics(corpus)
        return jsonify({"column": col, "keywords": keywords, "stats": stats})
    except Exception as e:
        return jsonify({"error": str(e)}), 500