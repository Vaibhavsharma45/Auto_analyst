"""
backend/routes/upload_routes.py
Handles file upload and manual CSV input
"""

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import uuid, os
from backend.utils.data_loader import load_dataframe, load_from_string, get_sample_info
from backend.utils.session_store import save_session

upload_bp = Blueprint("upload", __name__)

ALLOWED = {".csv", ".tsv", ".xlsx", ".xls", ".json", ".txt"}


@upload_bp.route("/file", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED:
        return jsonify({"error": f"Unsupported file type: {ext}"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    try:
        df = load_dataframe(filepath)
        session_id = str(uuid.uuid4())
        save_session(session_id, df, filename=filename)
        return jsonify({"session_id": session_id, "info": get_sample_info(df), "filename": filename})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@upload_bp.route("/text", methods=["POST"])
def upload_text():
    body = request.get_json()
    if not body or "text" not in body:
        return jsonify({"error": "No text provided"}), 400

    try:
        df = load_from_string(body["text"])
        session_id = str(uuid.uuid4())
        save_session(session_id, df, filename="pasted-data.csv")
        return jsonify({"session_id": session_id, "info": get_sample_info(df), "filename": "pasted-data.csv"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
