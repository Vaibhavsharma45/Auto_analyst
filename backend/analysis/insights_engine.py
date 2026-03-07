"""
backend/analysis/insights_engine.py
Step 5: Communicate Insights
Step 6: Recommend Actions
Supports both Anthropic Claude and Groq (free)
"""
import pandas as pd
import numpy as np
import os
import json

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass


def _get_provider():
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


class InsightsEngine:
    def __init__(self, df: pd.DataFrame, analysis: dict, goal: dict = None):
        self.df = df
        self.analysis = analysis
        self.goal = goal or {}

    def _build_summary(self) -> str:
        ov = self.analysis.get("overview", {})
        ns = self.analysis.get("numeric_stats", {})
        cs = self.analysis.get("categorical_stats", {})
        qr = self.analysis.get("quality_report", {})
        corr = self.analysis.get("correlations", {})
        sh = ov.get("shape", {})

        s = f"""Dataset: {sh.get('rows',0)} rows x {sh.get('columns',0)} cols
Goal: {self.goal.get('label','General')}
Question: {self.goal.get('question','Explore data')}
Quality: {qr.get('quality_score',0)}/100\n
NUMERIC:\n"""
        for col, stat in ns.items():
            s += f"  {col}: mean={stat.get('mean')}, std={stat.get('std')}, min={stat.get('min')}, max={stat.get('max')}, outliers={stat.get('outliers',{}).get('count',0)}\n"
        s += "\nCATEGORICAL:\n"
        for col, stat in cs.items():
            top = list(stat.get("value_counts", {}).items())[:3]
            s += f"  {col}: unique={stat.get('unique_values')}, top={top}\n"
        pairs = corr.get("strong_pairs", [])
        if pairs:
            s += f"\nSTRONG CORRELATIONS: {json.dumps(pairs[:4])}\n"
        issues = qr.get("issues", [])[:4]
        if issues:
            s += "\nISSUES:\n" + "\n".join(f"  [{i['severity']}] {i['message']}" for i in issues)
        s += f"\nSAMPLE:\n{self.df.head(3).to_string()}"
        return s

    def _call_ai(self, prompt: str) -> dict:
        provider, key = _get_provider()
        if not provider:
            return {"_error": "No API key found"}
        try:
            if provider == "anthropic":
                return self._call_anthropic(key, prompt)
            else:
                return self._call_groq(key, prompt)
        except Exception as e:
            return {"_error": str(e)}

    def _call_anthropic(self, key, prompt):
        import anthropic
        client = anthropic.Anthropic(api_key=key)
        r = client.messages.create(
            model="claude-sonnet-4-20250514", max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        text = r.content[0].text.strip().replace("```json","").replace("```","").strip()
        return json.loads(text)

    def _call_groq(self, key, prompt):
        import requests
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": "llama-3.3-70b-versatile", "messages": [
                {"role": "system", "content": "You are an expert data analyst. Always respond with valid JSON only, no markdown."},
                {"role": "user", "content": prompt}
            ], "max_tokens": 2000, "temperature": 0.7},
            timeout=45
        )
        if r.status_code != 200:
            raise Exception(f"Groq {r.status_code}: {r.text[:200]}")
        text = r.json()["choices"][0]["message"]["content"].strip()
        text = text.replace("```json","").replace("```","").strip()
        return json.loads(text)

    def generate_executive_summary(self) -> dict:
        prompt = f"""You are a senior data analyst writing an executive summary.

Dataset:
{self._build_summary()}

Return ONLY this JSON (no markdown, no extra text):
{{"headline":"One powerful sentence with the main finding","overview":"2-3 sentence dataset description","key_findings":[{{"finding":"specific insight with numbers","significance":"why it matters","type":"positive"}}],"data_story":"3-4 sentence narrative of what data reveals","anomalies":["unusual patterns"],"limitations":["data quality issues"]}}

Use real numbers. Be specific. Write like McKinsey analyst."""
        result = self._call_ai(prompt)
        if "_error" in result:
            return self._fallback_summary()
        return result

    def generate_data_story(self) -> dict:
        prompt = f"""You are a data storyteller.

Dataset:
{self._build_summary()}

Return ONLY this JSON (no markdown):
{{"title":"Compelling title","hook":"Opening with surprising insight","context":"Background","plot":"Main story arc","climax":"Most important finding","resolution":"What to do","conclusion":"Call to action","key_metrics":[{{"metric":"name","value":"number","context":"meaning"}}]}}

Use actual numbers. Be engaging. Use Hinglish naturally."""
        result = self._call_ai(prompt)
        if "_error" in result:
            return self._fallback_story()
        return result

    def generate_recommendations(self) -> dict:
        prompt = f"""You are a senior business analyst.

Dataset:
{self._build_summary()}

Return ONLY this JSON (no markdown):
{{"immediate_actions":[{{"action":"specific action","reason":"data evidence","impact":"high","effort":"low","metric":"how to measure","timeline":"immediate"}}],"strategic_recommendations":[{{"recommendation":"longer term suggestion","business_value":"expected benefit","data_evidence":"what supports this"}}],"data_collection_gaps":["additional data needed"],"next_analysis":["follow-up analyses"],"watch_out":["risks to monitor"]}}

Be specific. Reference actual column names and numbers."""
        result = self._call_ai(prompt)
        if "_error" in result:
            return self._fallback_recommendations()
        return result

    def _fallback_summary(self) -> dict:
        ns = self.analysis.get("numeric_stats", {})
        findings = [{"finding": f"{col}: mean={s.get('mean')}, range=[{s.get('min')},{s.get('max')}]",
                     "significance": "Key metric", "type": "neutral"}
                    for col, s in list(ns.items())[:3]]
        return {"headline": "Dataset analyzed — add API key for AI insights",
                "overview": f"{self.df.shape[0]} rows, {self.df.shape[1]} columns analyzed.",
                "key_findings": findings, "data_story": "Set GROQ_API_KEY or ANTHROPIC_API_KEY for AI insights.",
                "anomalies": [], "limitations": ["No API key configured"]}

    def _fallback_story(self) -> dict:
        return {"title": "Data Analysis Report", "hook": "Your data has been analyzed.",
                "context": f"{self.df.shape[0]} rows.", "plot": "Set API key for story.",
                "climax": "Analysis complete.", "resolution": "Review charts.",
                "conclusion": "Take action.", "key_metrics": []}

    def _fallback_recommendations(self) -> dict:
        recs = self.analysis.get("quality_report", {}).get("recommendations", [])
        return {"immediate_actions": [{"action": r, "reason": "Quality issue", "impact": "medium",
                                       "effort": "low", "metric": "Data quality %", "timeline": "immediate"}
                                      for r in recs[:3]],
                "strategic_recommendations": [], "data_collection_gaps": [],
                "next_analysis": [], "watch_out": []}
