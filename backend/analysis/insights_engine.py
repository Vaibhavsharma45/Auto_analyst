"""
backend/analysis/insights_engine.py
Step 5: Communicate Insights — AI-generated narrative & executive summary
Step 6: Recommend Actions — prioritized action items with business impact
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


class InsightsEngine:
    """
    Uses Claude AI to generate:
    - Executive Summary (Step 5: Communicate)
    - Action Recommendations (Step 6: Recommend)
    - Data Story / Narrative
    """

    def __init__(self, df: pd.DataFrame, analysis: dict, goal: dict = None):
        self.df = df
        self.analysis = analysis
        self.goal = goal or {}
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "")

    def _build_analysis_summary(self) -> str:
        ov = self.analysis.get("overview", {})
        ns = self.analysis.get("numeric_stats", {})
        cs = self.analysis.get("categorical_stats", {})
        qr = self.analysis.get("quality_report", {})
        corr = self.analysis.get("correlations", {})

        shape = ov.get("shape", {})
        summary = f"""Dataset: {shape.get('rows', 0)} rows x {shape.get('columns', 0)} columns
Goal: {self.goal.get('label', 'General Analysis')}
Business Question: {self.goal.get('question', 'Explore the data')}
Quality Score: {qr.get('quality_score', 0)}/100

NUMERIC COLUMNS STATS:"""
        for col, s in ns.items():
            summary += f"\n  {col}: mean={s.get('mean')}, std={s.get('std')}, min={s.get('min')}, max={s.get('max')}, outliers={s.get('outliers',{}).get('count',0)}, skew={s.get('skewness')}"

        summary += "\n\nCATEGORICAL COLUMNS:"
        for col, s in cs.items():
            top3 = list(s.get("value_counts", {}).items())[:3]
            summary += f"\n  {col}: {s.get('unique_values')} unique, top={top3}"

        strong_corr = corr.get("strong_pairs", [])
        if strong_corr:
            summary += f"\n\nSTRONG CORRELATIONS: {json.dumps(strong_corr[:5])}"

        issues = qr.get("issues", [])
        if issues:
            summary += f"\n\nDATA QUALITY ISSUES ({len(issues)}):"
            for i in issues[:5]:
                summary += f"\n  [{i['severity']}] {i['message']}"

        summary += f"\n\nSAMPLE DATA:\n{self.df.head(5).to_string()}"
        return summary

    def generate_executive_summary(self) -> dict:
        """Step 5: Communicate Insights — structured executive summary"""
        summary = self._build_analysis_summary()

        prompt = f"""You are a senior data analyst writing an executive summary.

Dataset Analysis:
{summary}

Write a professional executive summary in JSON format:
{{
  "headline": "One powerful sentence capturing the main finding",
  "overview": "2-3 sentence dataset description",
  "key_findings": [
    {{"finding": "specific insight with numbers", "significance": "why it matters", "type": "positive|negative|neutral"}}
  ],
  "data_story": "3-4 sentence narrative telling the story of what this data reveals — like a data journalist would write",
  "anomalies": ["any unusual patterns or outliers worth noting"],
  "limitations": ["data quality issues or analysis limitations to keep in mind"]
}}

Use actual numbers from the stats. Be specific. Write like a McKinsey analyst.
Respond ONLY with valid JSON, no markdown."""

        return self._call_claude(prompt, fallback=self._fallback_executive_summary())

    def generate_recommendations(self) -> dict:
        """Step 6: Recommend Actions — prioritized action items"""
        summary = self._build_analysis_summary()

        prompt = f"""You are a senior business analyst. Based on this data analysis, generate actionable recommendations.

Dataset Analysis:
{summary}

Generate recommendations in JSON format:
{{
  "immediate_actions": [
    {{
      "action": "specific action to take",
      "reason": "data evidence supporting this",
      "impact": "high|medium|low",
      "effort": "high|medium|low",
      "metric": "how to measure success",
      "timeline": "immediate|1 week|1 month|1 quarter"
    }}
  ],
  "strategic_recommendations": [
    {{
      "recommendation": "longer-term strategic suggestion",
      "business_value": "expected business benefit",
      "data_evidence": "what in the data supports this"
    }}
  ],
  "data_collection_gaps": ["what additional data would improve analysis"],
  "next_analysis": ["follow-up analyses that would add value"],
  "watch_out": ["risks or red flags to monitor"]
}}

Be very specific. Reference actual column names and numbers. Prioritize by impact.
Respond ONLY with valid JSON, no markdown."""

        return self._call_claude(prompt, fallback=self._fallback_recommendations())

    def generate_data_story(self) -> dict:
        """Full narrative data story for presentation"""
        summary = self._build_analysis_summary()

        prompt = f"""You are a data storyteller. Create a compelling narrative from this analysis.

Dataset Analysis:
{summary}

Write a data story in JSON:
{{
  "title": "Compelling title for this analysis",
  "hook": "Opening sentence that grabs attention with a surprising insight",
  "context": "Background: what this data represents",
  "plot": "The main story arc — what the data reveals step by step",
  "climax": "The most important finding",
  "resolution": "What should be done about it",
  "conclusion": "Call to action for decision makers",
  "key_metrics": [
    {{"metric": "name", "value": "number", "context": "what this means"}}
  ]
}}

Use Hinglish naturally. Be engaging, not dry. Reference specific numbers.
Respond ONLY with valid JSON, no markdown."""

        return self._call_claude(prompt, fallback=self._fallback_story())

    def _call_claude(self, prompt: str, fallback: dict) -> dict:
        if not self.api_key:
            return fallback
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            text = response.content[0].text.strip()
            text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception as e:
            fallback["_error"] = str(e)
            return fallback

    def _fallback_executive_summary(self) -> dict:
        ns = self.analysis.get("numeric_stats", {})
        qr = self.analysis.get("quality_report", {})
        findings = []
        for col, s in list(ns.items())[:3]:
            findings.append({
                "finding": f"{col}: mean={s.get('mean')}, range=[{s.get('min')}, {s.get('max')}]",
                "significance": "Key metric in dataset",
                "type": "neutral"
            })
        return {
            "headline": "Dataset analyzed successfully",
            "overview": f"Dataset with {self.df.shape[0]} rows and {self.df.shape[1]} columns.",
            "key_findings": findings,
            "data_story": "Add ANTHROPIC_API_KEY to .env for AI-generated insights.",
            "anomalies": [i["message"] for i in qr.get("issues", [])[:3]],
            "limitations": ["Set ANTHROPIC_API_KEY for full AI analysis"]
        }

    def _fallback_recommendations(self) -> dict:
        qr = self.analysis.get("quality_report", {})
        actions = []
        for rec in qr.get("recommendations", [])[:4]:
            actions.append({
                "action": rec, "reason": "Data quality issue detected",
                "impact": "medium", "effort": "low",
                "metric": "Data completeness %", "timeline": "immediate"
            })
        return {
            "immediate_actions": actions,
            "strategic_recommendations": [],
            "data_collection_gaps": ["Set ANTHROPIC_API_KEY for AI recommendations"],
            "next_analysis": [],
            "watch_out": []
        }

    def _fallback_story(self) -> dict:
        return {
            "title": "Data Analysis Report",
            "hook": "Your dataset has been analyzed.",
            "context": f"{self.df.shape[0]} rows, {self.df.shape[1]} columns.",
            "plot": "Set ANTHROPIC_API_KEY for AI-generated story.",
            "climax": "Analysis complete.",
            "resolution": "Review the statistics and charts.",
            "conclusion": "Take action based on the data.",
            "key_metrics": []
        }
