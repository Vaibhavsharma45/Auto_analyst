"""
backend/routes/chat_routes.py
AI Chatbot — supports Groq (free) and Anthropic Claude
Language: English or Hinglish based on frontend preference
"""
import os, json, re
from flask import Blueprint, request, jsonify
from backend.utils.session_store import get_session, get_df, apply_df_operation, update_session
from backend.analysis.eda_engine import EDAEngine

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass

chat_bp = Blueprint("chat", __name__)


def _get_provider():
    groq_key = os.getenv("GROQ_API_KEY", "")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    if groq_key.startswith("gsk_"): return "groq", groq_key
    if anthropic_key.startswith("sk-ant-"): return "anthropic", anthropic_key
    return None, None


def _build_data_context(session: dict) -> str:
    df = session["df"]
    analysis = session.get("analysis", {})
    num_stats = analysis.get("numeric_stats", {})
    cat_stats = analysis.get("categorical_stats", {})
    quality = analysis.get("quality_report", {})
    corr = analysis.get("correlations", {})
    overview = analysis.get("overview", {})

    ctx = f"""DATASET: {session.get('filename', 'dataset')}
Shape: {df.shape[0]} rows x {df.shape[1]} columns
Columns: {', '.join(df.columns.tolist())}
Numeric: {', '.join(df.select_dtypes(include='number').columns.tolist())}
Categorical: {', '.join(df.select_dtypes(include='object').columns.tolist())}
Missing: {overview.get('missing', {}).get('total_missing_cells', 0)} | Duplicates: {overview.get('duplicates', {}).get('duplicate_rows', 0)}
Quality Score: {quality.get('quality_score', 'N/A')}/100

NUMERIC STATS:
"""
    for col, s in num_stats.items():
        ctx += f"  {col}: mean={s.get('mean')}, std={s.get('std')}, min={s.get('min')}, max={s.get('max')}, outliers={s.get('outliers',{}).get('count',0)}\n"

    ctx += "\nCATEGORICAL:\n"
    for col, s in cat_stats.items():
        top = list(s.get("value_counts", {}).items())[:3]
        ctx += f"  {col}: unique={s.get('unique_values')}, top={top}\n"

    strong = corr.get("strong_pairs", [])
    if strong:
        ctx += f"\nSTRONG CORRELATIONS: {json.dumps(strong[:3])}\n"

    ctx += f"\nSAMPLE DATA:\n{df.head(3).to_string()}\n"
    return ctx


def _build_system_prompt(data_context: str, lang: str = "en") -> str:
    if lang == "hi":
        language_rule = """Language: Hinglish (natural Hindi + English mix). 
Example: "Is dataset mein 3 outliers hain salary column mein."
"""
    else:
        language_rule = """Language: Professional English only. Concise and precise.
Example: "The salary column contains 3 outliers above 2 standard deviations."
"""

    return f"""You are DataMind AI — an expert data analyst assistant.

{language_rule}

Dataset Context:
{data_context}

Response Rules:
- Keep answers SHORT and CONCISE — max 5-6 bullet points or 3-4 sentences
- Always use REAL NUMBERS from the dataset stats above
- Lead with the most important insight first
- No unnecessary preamble or filler phrases
- Use **bold** for key numbers and findings

For data transformation requests, respond with a JSON block:
```json
{{"action": "transform", "operation": "drop_duplicates", "params": {{}}}}
```
Supported operations: drop_column, rename_column, drop_duplicates, fill_missing, drop_missing, create_column, filter_rows, sort, normalize"""


@chat_bp.route("/message/<session_id>", methods=["POST"])
def chat_message(session_id):
    session = get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    body = request.get_json()
    if not body or "message" not in body:
        return jsonify({"error": "No message"}), 400

    user_message = body["message"]
    raw_history  = body.get("history", [])
    lang         = body.get("lang", "en")  # NEW — language from frontend

    data_context  = _build_data_context(session)
    system_prompt = _build_system_prompt(data_context, lang)

    messages = []
    for h in raw_history[-8:]:
        role = h.get("role", "")
        content = h.get("content", "")
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_message})

    provider, api_key = _get_provider()
    if not provider:
        return jsonify({"reply": _no_key_response(), "transform_result": None})

    try:
        reply = _call_groq(api_key, system_prompt, messages) if provider == "groq" else _call_anthropic(api_key, system_prompt, messages)

        # Handle transform actions
        transform_result = None
        if '```json' in reply and '"action": "transform"' in reply:
            try:
                match = re.search(r'```json\s*(\{.*?\})\s*```', reply, re.DOTALL)
                if match:
                    action = json.loads(match.group(1))
                    if action.get("action") == "transform":
                        transform_result = apply_df_operation(session_id, action.get("operation"), action.get("params", {}))
                        new_df = get_df(session_id)
                        if new_df is not None:
                            update_session(session_id, analysis=EDAEngine(new_df).run_full_analysis())
            except Exception:
                pass

        return jsonify({"reply": reply, "transform_result": transform_result})

    except Exception as e:
        return jsonify({"reply": f"❌ API Error: {str(e)}", "transform_result": None})


def _call_groq(api_key: str, system: str, messages: list) -> str:
    import requests
    full = [{"role": "system", "content": system}] + messages
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": "llama-3.3-70b-versatile", "messages": full, "max_tokens": 600, "temperature": 0.5},
        timeout=30
    )
    if r.status_code != 200:
        raise Exception(f"Groq {r.status_code}: {r.text[:200]}")
    return r.json()["choices"][0]["message"]["content"]


def _call_anthropic(api_key: str, system: str, messages: list) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=600,
        system=system,
        messages=messages
    )
    return response.content[0].text


def _no_key_response() -> str:
    return "⚠️ No API key configured. Add GROQ_API_KEY in environment variables. Get a free key at console.groq.com"