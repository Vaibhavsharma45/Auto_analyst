"""
backend/analysis/problem_engine.py
Step 1: Ask the Right Question
Step 2: Collect & Validate Data
"""
import pandas as pd
import numpy as np
from datetime import datetime


class ProblemEngine:
    """
    Guides user through defining the analysis problem
    and validates the dataset against the stated goal.
    """

    GOAL_TEMPLATES = {
        "sales_performance": {
            "label": "Sales Performance Analysis",
            "questions": [
                "Which products/regions are underperforming?",
                "What is the revenue trend over time?",
                "Are we hitting our targets?"
            ],
            "required_col_types": ["numeric", "categorical"],
            "kpis": ["Total Revenue", "Growth Rate", "Target Achievement %", "Top Products"]
        },
        "customer_analysis": {
            "label": "Customer Behaviour Analysis",
            "questions": [
                "Who are our best customers?",
                "What is the churn rate?",
                "Which segments are most profitable?"
            ],
            "required_col_types": ["numeric", "categorical"],
            "kpis": ["Customer Lifetime Value", "Churn Rate", "Segment Distribution", "Purchase Frequency"]
        },
        "hr_workforce": {
            "label": "HR / Workforce Analytics",
            "questions": [
                "What factors affect employee performance?",
                "Is there a pay gap?",
                "Which department has highest attrition?"
            ],
            "required_col_types": ["numeric", "categorical"],
            "kpis": ["Average Salary", "Performance Rating", "Attrition Rate", "Promotion Rate"]
        },
        "financial": {
            "label": "Financial Analysis",
            "questions": [
                "What is our profit margin trend?",
                "Which cost centers are inefficient?",
                "Are we meeting financial targets?"
            ],
            "required_col_types": ["numeric"],
            "kpis": ["Profit Margin", "Revenue Growth", "Cost Ratio", "ROI"]
        },
        "operations": {
            "label": "Operations / Supply Chain",
            "questions": [
                "Where are the bottlenecks?",
                "What is the defect/return rate?",
                "How can we optimize delivery times?"
            ],
            "required_col_types": ["numeric", "categorical"],
            "kpis": ["Cycle Time", "Defect Rate", "On-time Delivery %", "Inventory Turnover"]
        },
        "custom": {
            "label": "Custom Analysis",
            "questions": [],
            "required_col_types": [],
            "kpis": []
        }
    }

    def __init__(self, df: pd.DataFrame = None):
        self.df = df

    def get_goal_templates(self) -> dict:
        return self.GOAL_TEMPLATES

    def validate_data_for_goal(self, goal_type: str) -> dict:
        """Step 2: Validate if dataset is suitable for the stated goal"""
        if self.df is None:
            return {"valid": False, "error": "No dataset loaded"}

        df = self.df
        template = self.GOAL_TEMPLATES.get(goal_type, self.GOAL_TEMPLATES["custom"])
        issues = []
        warnings = []
        score = 100

        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

        # Check minimum rows
        if len(df) < 10:
            issues.append("Dataset has fewer than 10 rows — analysis may not be meaningful")
            score -= 30
        elif len(df) < 50:
            warnings.append(f"Only {len(df)} rows — larger dataset would give better insights")
            score -= 10

        # Check column types for goal
        if "numeric" in template["required_col_types"] and len(num_cols) == 0:
            issues.append("No numeric columns found — this analysis type requires numbers")
            score -= 40

        if "categorical" in template["required_col_types"] and len(cat_cols) == 0:
            warnings.append("No categorical columns found — grouping analysis will be limited")
            score -= 15

        # Missing values check
        missing_pct = df.isnull().mean().mean() * 100
        if missing_pct > 30:
            issues.append(f"High missing data: {missing_pct:.1f}% — clean before analysis")
            score -= 25
        elif missing_pct > 10:
            warnings.append(f"Moderate missing data: {missing_pct:.1f}% — consider imputation")
            score -= 10

        # Duplicate check
        dup_pct = df.duplicated().mean() * 100
        if dup_pct > 10:
            warnings.append(f"{dup_pct:.1f}% duplicate rows detected")
            score -= 5

        # Date column detection (useful for trend analysis)
        has_date = False
        for col in cat_cols:
            try:
                pd.to_datetime(df[col].head(10), infer_datetime_format=True)
                has_date = True
                break
            except Exception:
                pass

        return {
            "valid": len(issues) == 0,
            "score": max(0, score),
            "issues": issues,
            "warnings": warnings,
            "dataset_profile": {
                "rows": len(df),
                "columns": len(df.columns),
                "numeric_columns": num_cols,
                "categorical_columns": cat_cols,
                "has_datetime": has_date,
                "missing_pct": round(missing_pct, 2),
                "duplicate_pct": round(dup_pct, 2)
            },
            "suggested_analyses": self._suggest_analyses(goal_type, num_cols, cat_cols, has_date),
            "kpis": template["kpis"]
        }

    def _suggest_analyses(self, goal_type, num_cols, cat_cols, has_date) -> list:
        suggestions = []
        if num_cols:
            suggestions.append(f"Descriptive statistics for: {', '.join(num_cols[:3])}")
            if len(num_cols) >= 2:
                suggestions.append(f"Correlation between {num_cols[0]} and {num_cols[1]}")
        if cat_cols and num_cols:
            suggestions.append(f"Group {num_cols[0]} by {cat_cols[0]}")
        if has_date:
            suggestions.append("Time series trend analysis")
        if goal_type == "sales_performance":
            suggestions.append("Revenue by region/product breakdown")
            suggestions.append("Target vs Actual comparison")
        elif goal_type == "hr_workforce":
            suggestions.append("Salary distribution by department")
            suggestions.append("Performance vs Experience correlation")
        return suggestions
