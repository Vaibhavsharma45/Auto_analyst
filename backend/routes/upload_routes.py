"""
backend/routes/upload_routes.py
File upload with detailed error handling + 200MB limit
"""
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import uuid, os, traceback
from backend.utils.data_loader import load_dataframe, load_from_string, get_sample_info
from backend.utils.session_store import save_session

upload_bp = Blueprint("upload", __name__)
ALLOWED = {".csv", ".tsv", ".xlsx", ".xls", ".json", ".txt"}
MAX_SIZE_MB = 200
MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024


@upload_bp.route("/file", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file provided. Please select a file to upload."}), 400

    file = request.files["file"]
    if not file or file.filename == "":
        return jsonify({"error": "Empty file selected. Please choose a valid file."}), 400

    # Extension check
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED:
        return jsonify({
            "error": f"Unsupported file format: '{ext}'. Supported formats: CSV, TSV, Excel (.xlsx/.xls), JSON."
        }), 400

    # File size check
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    if size > MAX_SIZE_BYTES:
        mb = size / (1024 * 1024)
        return jsonify({
            "error": f"File too large: {mb:.1f} MB. Maximum allowed size is {MAX_SIZE_MB} MB."
        }), 400
    if size == 0:
        return jsonify({"error": "File is empty. Please upload a file with data."}), 400

    filename = secure_filename(file.filename)
    import tempfile
    filepath = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4().hex}_{filename}")
    file.save(filepath)

    try:
        df = load_dataframe(filepath)

        # Validation
        if df is None or len(df) == 0:
            return jsonify({"error": "File loaded but contains no data rows. Please check the file content."}), 400
        if len(df.columns) < 2:
            return jsonify({"error": f"File has only {len(df.columns)} column. A valid dataset needs at least 2 columns."}), 400
        if len(df) < 2:
            return jsonify({"error": f"File has only {len(df)} row of data. Please upload a dataset with more records."}), 400

        # Data quality warnings (don't block — just report)
        warnings = []
        miss = int(df.isnull().sum().sum())
        dups = int(df.duplicated().sum())
        if miss > 0:
            pct = round(miss / (df.shape[0] * df.shape[1]) * 100, 1)
            warnings.append(f"{miss} missing values found ({pct}% of data) — you can fill these in Step 3: Clean.")
        if dups > 0:
            warnings.append(f"{dups} duplicate rows found — you can remove these in Step 3: Clean.")

        session_id = str(uuid.uuid4())
        save_session(session_id, df, filename=filename)

        return jsonify({
            "session_id": session_id,
            "info": get_sample_info(df),
            "filename": filename,
            "size_mb": round(size / (1024 * 1024), 2),
            "warnings": warnings
        })

    except UnicodeDecodeError:
        return jsonify({"error": "File encoding error. Please save your file as UTF-8 and try again."}), 400
    except MemoryError:
        return jsonify({"error": "File too large to process in memory. Try a smaller file or reduce rows."}), 400
    except Exception as e:
        err = str(e)
        # Make error messages user-friendly
        if "No columns" in err or "no columns" in err:
            err = "Could not detect columns. Make sure the file has a header row and is properly formatted."
        elif "Excel" in err or "openpyxl" in err:
            err = "Excel file could not be read. Make sure the file is not corrupted or password-protected."
        elif "JSON" in err or "json" in err:
            err = "Invalid JSON format. The file must contain a JSON array or object."
        return jsonify({"error": f"Upload failed: {err}"}), 500
    finally:
        try:
            if os.path.exists(filepath): os.remove(filepath)
        except: pass


@upload_bp.route("/text", methods=["POST"])
def upload_text():
    body = request.get_json()
    if not body or "text" not in body:
        return jsonify({"error": "No text provided."}), 400

    text = body["text"].strip()
    if not text:
        return jsonify({"error": "Pasted text is empty."}), 400
    if len(text) > MAX_SIZE_BYTES:
        return jsonify({"error": f"Pasted text too large. Maximum {MAX_SIZE_MB} MB allowed."}), 400

    try:
        df = load_from_string(text)
        if df is None or len(df) == 0:
            return jsonify({"error": "No data found in pasted text. Check the CSV format."}), 400

        warnings = []
        miss = int(df.isnull().sum().sum())
        dups = int(df.duplicated().sum())
        if miss > 0:
            warnings.append(f"{miss} missing values found — fix in Step 3: Clean.")
        if dups > 0:
            warnings.append(f"{dups} duplicate rows found — remove in Step 3: Clean.")

        session_id = str(uuid.uuid4())
        save_session(session_id, df, filename="pasted-data.csv")
        return jsonify({
            "session_id": session_id,
            "info": get_sample_info(df),
            "filename": "pasted-data.csv",
            "warnings": warnings
        })
    except Exception as e:
        return jsonify({"error": f"Could not parse CSV: {str(e)}. Make sure the text is valid CSV format."}), 500