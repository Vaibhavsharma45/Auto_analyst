"""
backend/routes/chat_routes.py
AI chatbot — supports both Anthropic Claude and Groq (free)
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
    """Detect which AI provider to use based on available API key"""
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    groq_key = os.getenv("GROQ_API_KEY", "")

    if anthropic_key and anthropic_key.startswith("sk-ant-"):
        return "anthropic", anthropic_key
    elif groq_key and groq_key.startswith("gsk_"):
        return "groq", groq_key
    elif anthropic_key:
        return "anthropic", anthropic_key
    elif groq_key:
        return "groq", groq_key
    return None, None


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
Numeric: {', '.join(df.select_dtypes(include='number').columns.tolist())}
Categorical: {', '.join(df.select_dtypes(include='object').columns.tolist())}
Missing: {overview.get('missing', {}).get('total_missing_cells', 0)} cells
Duplicates: {overview.get('duplicates', {}).get('duplicate_rows', 0)}
Quality Score: {quality.get('quality_score', 'N/A')}/100\n
NUMERIC STATS:\n"""
    for col, s in num_stats.items():
        context += f"  {col}: mean={s.get('mean')}, std={s.get('std')}, min={s.get('min')}, max={s.get('max')}, outliers={s.get('outliers',{}).get('count',0)}, skew={s.get('skewness')}\n"

    context += "\nCATEGORICAL:\n"
    for col, s in cat_stats.items():
        top = list(s.get("value_counts", {}).items())[:4]
        context += f"  {col}: unique={s.get('unique_values')}, top={top}\n"

    strong = corr.get("strong_pairs", [])
    if strong:
        context += f"\nSTRONG CORRELATIONS: {json.dumps(strong[:4])}\n"

    issues = quality.get("issues", [])[:4]
    if issues:
        context += f"\nQUALITY ISSUES:\n" + "\n".join(f"  [{i['severity']}] {i['message']}" for i in issues)

    context += f"\nSAMPLE:\n{df.head(3).to_string()}\n"
    return context


def _build_system_prompt(data_context: str) -> str:
    return f"""You are DataMind AI, an expert data analyst and data scientist.
You are analyzing a dataset. Here is the complete context:

{data_context}

Your job:
1. Answer questions about the data accurately using the stats above
2. Provide actionable insights with specific numbers
3. Suggest transformations when relevant
4. Use Hinglish (Hindi + English mix) naturally
5. Remember conversation history

For transformation requests respond with JSON block:
```json
{{"action": "transform", "operation": "drop_duplicates", "params": {{}}}}
```

Operations: drop_column, rename_column, drop_duplicates, fill_missing, drop_missing, create_column, filter_rows, sort, normalize

Be specific with actual numbers. Use **bold** and bullet points."""


@chat_bp.route("/message/<session_id>", methods=["POST"])
def chat_message(session_id):
    session = get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    body = request.get_json()
    if not body or "message" not in body:
        return jsonify({"error": "No message"}), 400

    user_message = body["message"]
    raw_history = body.get("history", [])
    data_context = _build_data_context(session)
    system_prompt = _build_system_prompt(data_context)

    # Build valid message history
    messages = []
    for h in raw_history[-10:]:
        role = h.get("role", "")
        content = h.get("content", "")
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_message})

    provider, api_key = _get_provider()

    if not provider:
        return jsonify({
            "reply": _no_key_response(),
            "transform_result": None
        })

    try:
        if provider == "anthropic":
            reply = _call_anthropic(api_key, system_prompt, messages)
        else:
            reply = _call_groq(api_key, system_prompt, messages)

        # Handle transform actions
        transform_result = None
        if '```json' in reply and '"action": "transform"' in reply:
            try:
                match = re.search(r'```json\s*(\{.*?\})\s*```', reply, re.DOTALL)
                if match:
                    action = json.loads(match.group(1))
                    if action.get("action") == "transform":
                        transform_result = apply_df_operation(
                            session_id, action.get("operation"), action.get("params", {}))
                        new_df = get_df(session_id)
                        if new_df is not None:
                            update_session(session_id, analysis=EDAEngine(new_df).run_full_analysis())
            except Exception:
                pass

        return jsonify({"reply": reply, "transform_result": transform_result})

    except Exception as e:
        return jsonify({
            "reply": f"❌ **{provider.upper()} API Error:**\n\n`{str(e)}`\n\n**Check karo:**\n- `.env` mein key sahi hai?\n- Key active/valid hai?\n- Internet connection theek hai?",
            "transform_result": None
        })


def _call_anthropic(api_key: str, system: str, messages: list) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        system=system,
        messages=messages
    )
    return response.content[0].text


def _call_groq(api_key: str, system: str, messages: list) -> str:
    import requests
    # Groq uses OpenAI-compatible API
    full_messages = [{"role": "system", "content": system}] + messages
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",  # Best free Groq model
            "messages": full_messages,
            "max_tokens": 1500,
            "temperature": 0.7
        },
        timeout=30
    )
    if response.status_code != 200:
        raise Exception(f"Groq API {response.status_code}: {response.text[:200]}")
    return response.json()["choices"][0]["message"]["content"]


def _no_key_response() -> str:
    return """⚠️ **Koi API key nahi mili!**

`.env` file mein ek key add karo:

**Option 1 — Groq (FREE):**
```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxx
```
👉 Free key: console.groq.com

**Option 2 — Anthropic Claude:**
```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxx
```
👉 console.anthropic.com

Key add karne ke baad server restart karo:
`python app.py`"""
