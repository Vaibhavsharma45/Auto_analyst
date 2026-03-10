"""
backend/analysis/eda_engine.py
Core EDA Engine — performs full professional data analysis
like a senior data analyst would
"""

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings("ignore")


class EDAEngine:
    """
    Full-featured Exploratory Data Analysis engine.
    Covers: overview, univariate, bivariate, multivariate, quality checks.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        self.datetime_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()
        self._try_parse_dates()

    def _try_parse_dates(self):
        """Auto-detect and parse date columns"""
        for col in self.categorical_cols[:]:
            try:
                parsed = pd.to_datetime(self.df[col], infer_datetime_format=True)
                if parsed.notna().sum() > len(self.df) * 0.7:
                    self.df[col] = parsed
                    self.datetime_cols.append(col)
                    self.categorical_cols.remove(col)
            except Exception:
                pass

    # ─────────────────────────────────────────────
    # 1. DATASET OVERVIEW
    # ─────────────────────────────────────────────
    def get_overview(self) -> dict:
        df = self.df
        total_cells = df.shape[0] * df.shape[1]
        missing_cells = df.isnull().sum().sum()
        duplicate_rows = df.duplicated().sum()

        memory_usage = df.memory_usage(deep=True).sum()
        memory_mb = round(memory_usage / (1024 ** 2), 3)

        return {
            "shape": {"rows": int(df.shape[0]), "columns": int(df.shape[1])},
            "column_names": df.columns.tolist(),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "column_types": {
                "numeric": self.numeric_cols,
                "categorical": self.categorical_cols,
                "datetime": self.datetime_cols,
            },
            "missing": {
                "total_missing_cells": int(missing_cells),
                "missing_percentage": round(missing_cells / total_cells * 100, 2),
                "columns_with_missing": {
                    col: {"count": int(df[col].isnull().sum()),
                          "percentage": round(df[col].isnull().mean() * 100, 2)}
                    for col in df.columns if df[col].isnull().any()
                }
            },
            "duplicates": {
                "duplicate_rows": int(duplicate_rows),
                "duplicate_percentage": round(duplicate_rows / len(df) * 100, 2)
            },
            "memory_usage_mb": memory_mb,
            "data_completeness_pct": round((1 - missing_cells / total_cells) * 100, 2)
        }

    # ─────────────────────────────────────────────
    # 2. UNIVARIATE — NUMERIC
    # ─────────────────────────────────────────────
    def get_numeric_stats(self) -> dict:
        result = {}
        for col in self.numeric_cols:
            series = self.df[col].dropna()
            if len(series) == 0:
                continue

            q1, q3 = series.quantile(0.25), series.quantile(0.75)
            iqr = q3 - q1
            lower_fence = q1 - 1.5 * iqr
            upper_fence = q3 + 1.5 * iqr
            outliers = series[(series < lower_fence) | (series > upper_fence)]

            # Normality test (Shapiro-Wilk for n<=5000, else D'Agostino)
            if 3 <= len(series) <= 5000:
                stat, p_value = stats.shapiro(series.sample(min(len(series), 5000), random_state=42))
                normality_test = "shapiro-wilk"
            else:
                stat, p_value = stats.normaltest(series)
                normality_test = "dagostino-pearson"

            result[col] = {
                "count": int(series.count()),
                "missing": int(self.df[col].isnull().sum()),
                "missing_pct": round(self.df[col].isnull().mean() * 100, 2),
                "mean": round(float(series.mean()), 4),
                "median": round(float(series.median()), 4),
                "mode": round(float(series.mode()[0]), 4) if not series.mode().empty else None,
                "std": round(float(series.std()), 4),
                "variance": round(float(series.var()), 4),
                "min": round(float(series.min()), 4),
                "max": round(float(series.max()), 4),
                "range": round(float(series.max() - series.min()), 4),
                "q1": round(float(q1), 4),
                "q3": round(float(q3), 4),
                "iqr": round(float(iqr), 4),
                "skewness": round(float(series.skew()), 4),
                "kurtosis": round(float(series.kurtosis()), 4),
                "cv": round(float(series.std() / series.mean() * 100), 2) if series.mean() != 0 else None,
                "outliers": {
                    "count": int(len(outliers)),
                    "percentage": round(len(outliers) / len(series) * 100, 2),
                    "lower_fence": round(float(lower_fence), 4),
                    "upper_fence": round(float(upper_fence), 4),
                    "values": outliers.tolist()[:20]
                },
                "percentiles": {
                    "p1": round(float(series.quantile(0.01)), 4),
                    "p5": round(float(series.quantile(0.05)), 4),
                    "p10": round(float(series.quantile(0.10)), 4),
                    "p25": round(float(q1), 4),
                    "p50": round(float(series.quantile(0.50)), 4),
                    "p75": round(float(q3), 4),
                    "p90": round(float(series.quantile(0.90)), 4),
                    "p95": round(float(series.quantile(0.95)), 4),
                    "p99": round(float(series.quantile(0.99)), 4),
                },
                "normality": {
                    "test": normality_test,
                    "statistic": round(float(stat), 4),
                    "p_value": round(float(p_value), 4),
                    "is_normal": bool(p_value > 0.05)
                },
                "distribution": {
                    "is_symmetric": abs(float(series.skew())) < 0.5,
                    "skew_direction": "right" if float(series.skew()) > 0.5 else "left" if float(series.skew()) < -0.5 else "symmetric",
                    "tail_heaviness": "heavy" if float(series.kurtosis()) > 1 else "light" if float(series.kurtosis()) < -1 else "normal"
                }
            }
        return result

    # ─────────────────────────────────────────────
    # 3. UNIVARIATE — CATEGORICAL
    # ─────────────────────────────────────────────
    def get_categorical_stats(self) -> dict:
        result = {}
        for col in self.categorical_cols:
            series = self.df[col].dropna()
            if len(series) == 0:
                continue

            value_counts = series.value_counts()
            value_pcts = series.value_counts(normalize=True) * 100

            result[col] = {
                "count": int(series.count()),
                "missing": int(self.df[col].isnull().sum()),
                "missing_pct": round(self.df[col].isnull().mean() * 100, 2),
                "unique_values": int(series.nunique()),
                "cardinality_ratio": round(series.nunique() / len(series) * 100, 2),
                "top_value": str(value_counts.index[0]) if len(value_counts) > 0 else None,
                "top_value_count": int(value_counts.iloc[0]) if len(value_counts) > 0 else None,
                "top_value_pct": round(float(value_pcts.iloc[0]), 2) if len(value_pcts) > 0 else None,
                "value_counts": {str(k): int(v) for k, v in value_counts.items()},
                "value_percentages": {str(k): round(float(v), 2) for k, v in value_pcts.items()},
                "entropy": round(float(stats.entropy(value_counts.values / value_counts.sum())), 4),
                "is_binary": bool(series.nunique() == 2),
                "is_high_cardinality": bool(series.nunique() / len(series) > 0.5)
            }
        return result

    # ─────────────────────────────────────────────
    # 4. BIVARIATE — CORRELATION
    # ─────────────────────────────────────────────
    def get_correlations(self) -> dict:
        if len(self.numeric_cols) < 2:
            return {"error": "Need at least 2 numeric columns"}

        num_df = self.df[self.numeric_cols].dropna()

        pearson = num_df.corr(method="pearson").round(4)
        spearman = num_df.corr(method="spearman").round(4)
        kendall = num_df.corr(method="kendall").round(4)

        # Find highly correlated pairs
        strong_pairs = []
        for i in range(len(self.numeric_cols)):
            for j in range(i + 1, len(self.numeric_cols)):
                c1, c2 = self.numeric_cols[i], self.numeric_cols[j]
                r = float(pearson.loc[c1, c2])
                if abs(r) >= 0.5:
                    strong_pairs.append({
                        "col1": c1, "col2": c2,
                        "pearson_r": round(r, 4),
                        "strength": "very strong" if abs(r) >= 0.9 else "strong" if abs(r) >= 0.7 else "moderate",
                        "direction": "positive" if r > 0 else "negative"
                    })

        return {
            "pearson": {col: {c: float(v) for c, v in row.items()} for col, row in pearson.to_dict().items()},
            "spearman": {col: {c: float(v) for c, v in row.items()} for col, row in spearman.to_dict().items()},
            "kendall": {col: {c: float(v) for c, v in row.items()} for col, row in kendall.to_dict().items()},
            "strong_pairs": sorted(strong_pairs, key=lambda x: abs(x["pearson_r"]), reverse=True)
        }

    # ─────────────────────────────────────────────
    # 5. BIVARIATE — CATEGORICAL vs NUMERIC (ANOVA)
    # ─────────────────────────────────────────────
    def get_group_analysis(self) -> dict:
        result = {}
        for cat in self.categorical_cols[:3]:
            for num in self.numeric_cols[:4]:
                key = f"{cat}_vs_{num}"
                groups = [g[num].dropna().values for _, g in self.df.groupby(cat) if len(g[num].dropna()) >= 3]
                if len(groups) < 2:
                    continue
                try:
                    f_stat, p_val = stats.f_oneway(*groups)
                    group_stats = self.df.groupby(cat)[num].agg(["mean", "median", "std", "count"]).round(3)
                    result[key] = {
                        "categorical": cat,
                        "numeric": num,
                        "anova_f_stat": round(float(f_stat), 4),
                        "anova_p_value": round(float(p_val), 4),
                        "significant_difference": bool(p_val < 0.05),
                        "group_stats": group_stats.reset_index().to_dict("records")
                    }
                except Exception:
                    pass
        # Sanitize NaN/Inf values before returning — JSON doesn't support them
        import math
        def _sanitize(obj):
            if isinstance(obj, dict): return {k: _sanitize(v) for k,v in obj.items()}
            if isinstance(obj, list): return [_sanitize(v) for v in obj]
            if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)): return None
            return obj
        return _sanitize(result)

    # ─────────────────────────────────────────────
    # 6. DATA QUALITY REPORT
    # ─────────────────────────────────────────────
    def get_quality_report(self) -> dict:
        issues = []
        recommendations = []
        quality_score = 100

        df = self.df

        # Missing values
        missing_pct = df.isnull().mean() * 100
        for col, pct in missing_pct[missing_pct > 0].items():
            quality_score -= min(pct * 0.3, 15)
            severity = "critical" if pct > 30 else "warning" if pct > 10 else "info"
            issues.append({
                "type": "missing_values", "column": col,
                "severity": severity,
                "message": f"Column '{col}' has {pct:.1f}% missing values ({df[col].isnull().sum()} rows)"
            })
            if pct > 50:
                recommendations.append(f"Consider dropping column '{col}' (>{pct:.0f}% missing)")
            elif pct > 10:
                recommendations.append(f"Impute '{col}' with {'median' if col in self.numeric_cols else 'mode'}")

        # Duplicates
        dups = df.duplicated().sum()
        if dups > 0:
            quality_score -= min(dups / len(df) * 50, 10)
            issues.append({
                "type": "duplicates", "column": "all",
                "severity": "warning",
                "message": f"{dups} duplicate rows found ({dups/len(df)*100:.1f}%)"
            })
            recommendations.append(f"Remove {dups} duplicate rows with df.drop_duplicates()")

        # Outliers
        for col in self.numeric_cols:
            series = df[col].dropna()
            q1, q3 = series.quantile(0.25), series.quantile(0.75)
            iqr = q3 - q1
            outlier_count = ((series < q1 - 1.5*iqr) | (series > q3 + 1.5*iqr)).sum()
            if outlier_count > 0:
                pct = outlier_count / len(series) * 100
                quality_score -= min(pct * 0.2, 5)
                issues.append({
                    "type": "outliers", "column": col,
                    "severity": "warning" if pct > 5 else "info",
                    "message": f"Column '{col}' has {outlier_count} outliers ({pct:.1f}%)"
                })

        # High cardinality
        for col in self.categorical_cols:
            cardinality = df[col].nunique() / len(df)
            if cardinality > 0.8:
                issues.append({
                    "type": "high_cardinality", "column": col,
                    "severity": "info",
                    "message": f"Column '{col}' may be an ID column ({df[col].nunique()} unique values)"
                })

        # Skewness
        for col in self.numeric_cols:
            skew = abs(df[col].skew())
            if skew > 2:
                issues.append({
                    "type": "high_skewness", "column": col,
                    "severity": "info",
                    "message": f"Column '{col}' is highly skewed (skewness={df[col].skew():.2f}). Consider log transform."
                })
                recommendations.append(f"Apply np.log1p() to '{col}' to reduce skewness ({df[col].skew():.2f})")

        return {
            "quality_score": max(0, round(quality_score, 1)),
            "total_issues": len(issues),
            "issues": issues,
            "recommendations": recommendations,
            "summary": {
                "critical": sum(1 for i in issues if i["severity"] == "critical"),
                "warning": sum(1 for i in issues if i["severity"] == "warning"),
                "info": sum(1 for i in issues if i["severity"] == "info")
            }
        }

    # ─────────────────────────────────────────────
    # 7. MULTIVARIATE — PCA SUMMARY
    # ─────────────────────────────────────────────
    def get_pca_summary(self) -> dict:
        from sklearn.preprocessing import StandardScaler
        from sklearn.decomposition import PCA

        if len(self.numeric_cols) < 3:
            return {"available": False, "reason": "Need 3+ numeric columns"}

        try:
            num_df = self.df[self.numeric_cols].dropna()
            scaler = StandardScaler()
            scaled = scaler.fit_transform(num_df)
            n_components = min(len(self.numeric_cols), 5)
            pca = PCA(n_components=n_components)
            pca.fit(scaled)

            explained = pca.explained_variance_ratio_
            cumulative = np.cumsum(explained)

            return {
                "available": True,
                "n_components_analyzed": n_components,
                "explained_variance_ratio": [round(float(v), 4) for v in explained],
                "cumulative_variance": [round(float(v), 4) for v in cumulative],
                "components_for_90pct": int(np.argmax(cumulative >= 0.90) + 1),
                "loadings": {
                    f"PC{i+1}": {col: round(float(v), 4) for col, v in zip(self.numeric_cols, pca.components_[i])}
                    for i in range(n_components)
                }
            }
        except Exception as e:
            return {"available": False, "reason": str(e)}

    # ─────────────────────────────────────────────
    # 8. TIME SERIES (if datetime cols exist)
    # ─────────────────────────────────────────────
    def get_time_series_analysis(self) -> dict:
        if not self.datetime_cols or not self.numeric_cols:
            return {"available": False}

        date_col = self.datetime_cols[0]
        results = {}

        try:
            ts_df = self.df[[date_col] + self.numeric_cols[:3]].copy()
            ts_df = ts_df.set_index(date_col).sort_index()

            for col in self.numeric_cols[:3]:
                series = ts_df[col].dropna()
                if len(series) < 4:
                    continue
                results[col] = {
                    "date_range": {
                        "start": str(series.index.min()),
                        "end": str(series.index.max())
                    },
                    "monthly_mean": ts_df[col].resample("ME").mean().dropna().round(2).to_dict() if hasattr(ts_df[col].resample("ME"), "mean") else {},
                    "trend": "increasing" if series.iloc[-1] > series.iloc[0] else "decreasing"
                }
        except Exception as e:
            return {"available": False, "reason": str(e)}

        return {"available": True, "date_column": date_col, "analysis": results}

    # ─────────────────────────────────────────────
    # FULL ANALYSIS — runs everything
    # ─────────────────────────────────────────────
    def run_full_analysis(self) -> dict:
        return {
            "overview": self.get_overview(),
            "numeric_stats": self.get_numeric_stats(),
            "categorical_stats": self.get_categorical_stats(),
            "correlations": self.get_correlations(),
            "group_analysis": self.get_group_analysis(),
            "quality_report": self.get_quality_report(),
            "pca_summary": self.get_pca_summary(),
            "time_series": self.get_time_series_analysis(),
        }