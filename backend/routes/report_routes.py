"""
backend/routes/report_routes.py
"""
import os, uuid
from flask import Blueprint, jsonify, send_file, current_app
from backend.utils.session_store import get_session, get_df
from backend.analysis.eda_engine import EDAEngine
from backend.analysis.chart_generator import ChartGenerator
from backend.analysis.report_generator import ReportGenerator

report_bp = Blueprint("report", __name__)

@report_bp.route("/pdf/<session_id>", methods=["GET"])
def download_pdf(session_id):
    session = get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    df = session["df"]
    analysis = session.get("analysis") or EDAEngine(df).run_full_analysis()
    charts = session.get("charts") or ChartGenerator(df).generate_all()
    filename = session.get("filename", "dataset")

    output_path = os.path.join(
        current_app.config["REPORTS_FOLDER"],
        f"report_{uuid.uuid4().hex[:8]}.pdf"
    )

    try:
        gen = ReportGenerator(df, analysis, charts, filename)
        gen.generate_pdf(output_path)
        return send_file(output_path, mimetype="application/pdf",
                         as_attachment=True, download_name="datamind-report.pdf")
    except Exception as e:
        return jsonify({"error": str(e)}), 500
