"""
backend/routes/workflow_routes.py
Routes for Step 1 (Problem Definition), Step 2 (Data Validation),
Step 5 (Communicate Insights), Step 6 (Recommend Actions)
"""
from flask import Blueprint, request, jsonify
from backend.utils.session_store import get_session, get_df, update_session
from backend.analysis.problem_engine import ProblemEngine
from backend.analysis.insights_engine import InsightsEngine
from backend.analysis.eda_engine import EDAEngine

workflow_bp = Blueprint("workflow", __name__)


# ── STEP 1: Problem Definition ────────────────────────────────────────
@workflow_bp.route("/goals", methods=["GET"])
def get_goals():
    """Return available goal/problem templates"""
    engine = ProblemEngine()
    return jsonify(engine.get_goal_templates())


@workflow_bp.route("/set-goal/<session_id>", methods=["POST"])
def set_goal(session_id):
    """Save the user's analysis goal to session"""
    session = get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    body = request.get_json()
    goal = {
        "type": body.get("type", "custom"),
        "label": body.get("label", "Custom Analysis"),
        "question": body.get("question", ""),
        "kpis": body.get("kpis", []),
        "audience": body.get("audience", ""),
        "deadline": body.get("deadline", "")
    }
    update_session(session_id, goal=goal)
    return jsonify({"success": True, "goal": goal})


@workflow_bp.route("/get-goal/<session_id>", methods=["GET"])
def get_goal(session_id):
    session = get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404
    return jsonify(session.get("goal", {}))


# ── STEP 2: Data Validation ───────────────────────────────────────────
@workflow_bp.route("/validate/<session_id>", methods=["POST"])
def validate_data(session_id):
    """Validate dataset suitability for the stated goal"""
    df = get_df(session_id)
    if df is None:
        return jsonify({"error": "Session not found"}), 404

    body = request.get_json() or {}
    goal_type = body.get("goal_type", "custom")

    engine = ProblemEngine(df)
    result = engine.validate_data_for_goal(goal_type)
    return jsonify(result)


# ── STEP 5: Communicate Insights ─────────────────────────────────────
@workflow_bp.route("/executive-summary/<session_id>", methods=["GET"])
def executive_summary(session_id):
    session = get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    df = session["df"]
    analysis = session.get("analysis")
    if not analysis:
        analysis = EDAEngine(df).run_full_analysis()
        update_session(session_id, analysis=analysis)

    goal = session.get("goal", {})
    engine = InsightsEngine(df, analysis, goal)
    result = engine.generate_executive_summary()
    return jsonify(result)


@workflow_bp.route("/data-story/<session_id>", methods=["GET"])
def data_story(session_id):
    session = get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    df = session["df"]
    analysis = session.get("analysis") or EDAEngine(df).run_full_analysis()
    goal = session.get("goal", {})
    engine = InsightsEngine(df, analysis, goal)
    result = engine.generate_data_story()
    return jsonify(result)


# ── STEP 6: Recommend Actions ─────────────────────────────────────────
@workflow_bp.route("/recommendations/<session_id>", methods=["GET"])
def recommendations(session_id):
    session = get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    df = session["df"]
    analysis = session.get("analysis") or EDAEngine(df).run_full_analysis()
    goal = session.get("goal", {})
    engine = InsightsEngine(df, analysis, goal)
    result = engine.generate_recommendations()
    return jsonify(result)


# ── FULL WORKFLOW STATUS ───────────────────────────────────────────────
@workflow_bp.route("/status/<session_id>", methods=["GET"])
def workflow_status(session_id):
    """Return which workflow steps are complete"""
    session = get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    df = session.get("df")
    analysis = session.get("analysis", {})
    goal = session.get("goal", {})
    charts = session.get("charts", {})

    return jsonify({
        "step1_problem": bool(goal.get("question")),
        "step2_data": df is not None,
        "step3_clean": bool(analysis.get("quality_report")),
        "step4_analyze": bool(analysis.get("numeric_stats") or analysis.get("categorical_stats")),
        "step5_communicate": False,  # Generated on demand
        "step6_recommend": False,    # Generated on demand
        "goal": goal,
        "data_shape": [int(df.shape[0]), int(df.shape[1])] if df is not None else None,
        "quality_score": analysis.get("quality_report", {}).get("quality_score", 0)
    })
