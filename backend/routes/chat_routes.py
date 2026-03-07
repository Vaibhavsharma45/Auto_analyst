"""
backend/routes/chat_routes.py
AI chatbot powered by Claude — fixed version
"""
import os
import json
import re
from flask import Blueprint, request, jsonify
from backend.utils.session_store import get_session, get_df, apply_df_operation, update_session
from backend.analysis.eda_engine import EDAEngine

# Load .env BEFORE reading any env vars
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass

chat_bp = Blueprint("chat", __name__)


def _get_api_key():
    """Read API key fresh on every request"""
    return os.getenv("ANTHROPIC_API_KEY", "")


def _build_data_context(session: dict) -> str:
    df = session["df"]
    analysis = session.get("analysis", {})
    overview = analysis.get("overview", {})
    num_stats = analysis.get("numeric_stats", {})
    cat_stats = analysis.get("categorical_stats", {})
    quality = analysis.get("quality_report", {})
    corr = analysis.get("correlations", {})

    context = f"""DATASET: {session.get('filename', 'dataset')}
Shape: {df.shape[0]} rows x {df.shape[1]} columns
Columns: {', '.join(df.columns.tolist())}
Numeric columns: {', '.join(df.select_dtypes(include='number').columns.tolist())}
Categorical columns: {', '.join(df.select_dtypes(include='object').columns.tolist())}
Missing cells: {overview.get('missing', {}).get('total_missing_cells', 0)} ({overview.get('missing', {}).get('missing_percentage', 0):.1f}%)
Duplicate rows: {overview.get('duplicates', {}).get('duplicate_rows', 0)}
Data Quality Score: {quality.get('quality_score', 'N/A')}/100

NUMERIC STATISTICS:
"""
    for col, stats in num_stats.items():
        context += (f"  {col}: mean={stats.get('mean')}, median={stats.get('median')}, "
                    f"std={stats.get('std')}, min={stats.get('min')}, max={stats.get('max')}, "
                    f"outliers={stats.get('outliers', {}).get('count', 0)}, skew={stats.get('skewness')}\n")

    context += "\nCATEGORICAL STATISTICS:\n"
    for col, stats in cat_stats.items():
        top = list(stats.get("value_counts", {}).items())[:5]
        context += f"  {col}: unique={stats.get('unique_values')}, top_values={top}\n"

    strong = corr.get("strong_pairs", [])
    if strong:
        context += f"\nSTRONG CORRELATIONS: {json.dumps(strong[:5])}\n"

    issues = quality.get("issues", [])
    if issues:
        context += f"\nQUALITY ISSUES: {len(issues)} found\n"
        for issue in issues[:5]:
            context += f"  [{issue['severity']}] {issue['message']}\n"

    context += f"\nFIRST 3 ROWS SAMPLE:\n{df.head(3).to_string()}\n"
    return context


@chat_bp.route("/message/<session_id>", methods=["POST"])
def chat_message(session_id):
    session = get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found or expired. Please reload your data."}), 404

    body = request.get_json()
    if not body or "message" not in body:
        return jsonify({"error": "No message provided"}), 400

    user_message = body["message"]
    raw_history = body.get("history", [])
    data_context = _build_data_context(session)

    system_prompt = f"""You are DataMind AI, an expert data analyst and data scientist.
You are analyzing a dataset loaded by the user. Here is the complete dataset context:

{data_context}

Your job:
1. Answer any question about the data accurately using the statistics above
2. Provide actionable insights and recommendations
3. Suggest data transformations when relevant
4. Explain statistical concepts clearly
5. Use Hinglish (Hindi + English mix) naturally since the user is from India
6. Remember previous messages and maintain conversation context

For transformation requests, respond with a JSON block like:
```json
{{"action": "transform", "operation": "drop_duplicates", "params": {{}}}}
```

Available operations:
- drop_column: {{"column": "col_name"}}
- rename_column: {{"old_name": "x", "new_name": "y"}}
- drop_duplicates: {{}}
- fill_missing: {{"column": "col", "method": "mean|median|mode|zero|forward|backward"}}
- drop_missing: {{"column": "col_name"}} or {{}} for all
- create_column: {{"name": "new_col", "expression": "col1 + col2"}}
- filter_rows: {{"expression": "age > 25"}}
- sort: {{"column": "col_name", "ascending": true}}
- normalize: {{"column": "col_name", "method": "minmax|zscore|log"}}

Be specific, data-driven, and use actual numbers from the statistics provided.
Format responses with **bold** and bullet points where helpful."""

    # Build messages array with only valid roles
    messages = []
    for h in raw_history[-10:]:
        role = h.get("role", "")
        content = h.get("content", "")
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_message})

    api_key = _get_api_key()

    if not api_key:
        return jsonify({
            "reply": _fallback_response(user_message, session),
            "transform_result": None,
            "warning": "ANTHROPIC_API_KEY not set"
        })

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            system=system_prompt,
            messages=messages
        )
        reply = response.content[0].text

        transform_result = None
        if '```json' in reply and '"action": "transform"' in reply:
            try:
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', reply, re.DOTALL)
                if json_match:
                    action_data = json.loads(json_match.group(1))
                    if action_data.get("action") == "transform":
                        transform_result = apply_df_operation(
                            session_id,
                            action_data.get("operation"),
                            action_data.get("params", {})
                        )
                        new_df = get_df(session_id)
                        if new_df is not None:
                            new_analysis = EDAEngine(new_df).run_full_analysis()
                            update_session(session_id, analysis=new_analysis)
            except Exception:
                pass

        return jsonify({"reply": reply, "transform_result": transform_result})

    except Exception as e:
        return jsonify({
            "reply": f"❌ API Error: {str(e)}\n\nCheck karo `.env` mein `ANTHROPIC_API_KEY` sahi hai aur server restart karo.",
            "transform_result": None
        })


def _fallback_response(message: str, session: dict) -> str:
    df = session["df"]
    analysis = session.get("analysis", {})
    msg_lower = message.lower()

    if any(w in msg_lower for w in ["summary", "overview", "describe", "batao", "kya hai"]):
        overview = analysis.get("overview", {})
        shape = overview.get("shape", {})
        return (f"📊 **Dataset Summary:**\n\n"
                f"- **Rows:** {shape.get('rows', len(df)):,}\n"
                f"- **Columns:** {shape.get('columns', len(df.columns))}\n"
                f"- **Columns:** {', '.join(df.columns.tolist())}\n"
                f"- **Missing values:** {overview.get('missing', {}).get('total_missing_cells', 0):,}\n"
                f"- **Quality Score:** {analysis.get('quality_report', {}).get('quality_score', 'N/A')}/100")

    return (f"⚠️ **ANTHROPIC_API_KEY not found in .env!**\n\n"
            f"`.env` file mein ye line add karo:\n"
            f"`ANTHROPIC_API_KEY=sk-ant-...`\n\n"
            f"Phir server restart karo.")
