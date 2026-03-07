"""
DataMind Pro — AI-Powered Data Analysis Platform
Main Flask Application Entry Point
"""

from flask import Flask
from flask_cors import CORS
import sys, os

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.routes.upload_routes import upload_bp
from backend.routes.analysis_routes import analysis_bp
from backend.routes.chart_routes import chart_bp
from backend.routes.report_routes import report_bp
from backend.routes.chat_routes import chat_bp
from backend.routes.workflow_routes import workflow_bp

def create_app():
    app = Flask(
        __name__,
        template_folder="frontend/templates",
        static_folder="frontend/static"
    )
    app.config["UPLOAD_FOLDER"] = "data/uploads"
    app.config["REPORTS_FOLDER"] = "reports/output"
    app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024
    app.secret_key = "datamind-secret-key-change-in-prod"

    CORS(app)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["REPORTS_FOLDER"], exist_ok=True)

    app.register_blueprint(upload_bp,      url_prefix="/api/upload")
    app.register_blueprint(analysis_bp,    url_prefix="/api/analysis")
    app.register_blueprint(chart_bp,       url_prefix="/api/charts")
    app.register_blueprint(report_bp,      url_prefix="/api/report")
    app.register_blueprint(chat_bp,        url_prefix="/api/chat")
    app.register_blueprint(workflow_bp,    url_prefix="/api/workflow")

    from flask import render_template
    @app.route("/")
    def index():
        return render_template("index.html")

    return app

if __name__ == "__main__":
    app = create_app()
    print("\n🚀 DataMind Pro starting at http://localhost:5000\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
