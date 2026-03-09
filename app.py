"""DataMind Pro v3 — Main Flask App"""
from flask import Flask
from flask_cors import CORS
import sys, os

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.routes.upload_routes   import upload_bp
from backend.routes.analysis_routes import analysis_bp
from backend.routes.chart_routes    import chart_bp
from backend.routes.report_routes   import report_bp
from backend.routes.chat_routes     import chat_bp
from backend.routes.workflow_routes import workflow_bp
from backend.routes.ml_routes       import ml_bp
from backend.routes.extras_routes   import extras_bp
from backend.routes.auth_routes     import auth_bp

def create_app():
    app = Flask(__name__, template_folder="frontend/templates", static_folder="frontend/static")
    app.config.update(
        UPLOAD_FOLDER=os.getenv("UPLOAD_FOLDER", "data/uploads"),
        REPORTS_FOLDER=os.getenv("REPORTS_FOLDER", "reports/output"),
        MAX_CONTENT_LENGTH=100*1024*1024,
        SECRET_KEY=os.getenv("SECRET_KEY", "datamind-v3-secret-key"),
        SESSION_COOKIE_SAMESITE="Lax"
    )
    CORS(app, supports_credentials=True, origins=[
    "http://localhost:5000",
    "http://127.0.0.1:5000", 
    "https://*.vercel.app",
    "https://*.onrender.com"
])
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["REPORTS_FOLDER"], exist_ok=True)
    os.makedirs("data", exist_ok=True)

    app.register_blueprint(upload_bp,   url_prefix="/api/upload")
    app.register_blueprint(analysis_bp, url_prefix="/api/analysis")
    app.register_blueprint(chart_bp,    url_prefix="/api/charts")
    app.register_blueprint(report_bp,   url_prefix="/api/report")
    app.register_blueprint(chat_bp,     url_prefix="/api/chat")
    app.register_blueprint(workflow_bp, url_prefix="/api/workflow")
    app.register_blueprint(ml_bp,       url_prefix="/api/ml")
    app.register_blueprint(extras_bp,   url_prefix="/api/extras")
    app.register_blueprint(auth_bp,     url_prefix="/api/auth")

    from flask import render_template, jsonify
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})

    return app

# For gunicorn — must be module-level
app = create_app()

if __name__ == "__main__":
    print("\n⚡ DataMind Pro v3 → http://localhost:5000\n")
    app.run(debug=True, host="0.0.0.0", port=5000)