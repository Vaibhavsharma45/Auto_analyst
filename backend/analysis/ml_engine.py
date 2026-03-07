"""
backend/analysis/ml_engine.py
ML Predictions — Regression, Classification, Clustering, Forecasting
"""
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor
from sklearn.cluster import KMeans
from sklearn.metrics import (mean_squared_error, r2_score, mean_absolute_error,
                              accuracy_score, classification_report, silhouette_score)
from sklearn.impute import SimpleImputer
import json


class MLEngine:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    def _prepare_features(self, feature_cols: list, target_col: str):
        """Prepare X, y with encoding and imputation"""
        df = self.df.copy()
        X_cols = [c for c in feature_cols if c != target_col]

        # Encode categoricals
        for col in X_cols:
            if df[col].dtype == object:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))

        X = df[X_cols].values
        y = df[target_col].values

        # Impute missing
        imp = SimpleImputer(strategy="mean")
        X = imp.fit_transform(X)
        y_imp = SimpleImputer(strategy="mean")
        y = y_imp.fit_transform(y.reshape(-1,1)).ravel()

        return X, y, X_cols

    # ─── REGRESSION ──────────────────────────────────────
    def run_regression(self, target_col: str, feature_cols: list = None) -> dict:
        if target_col not in self.numeric_cols:
            return {"error": f"'{target_col}' must be numeric for regression"}

        if feature_cols is None:
            feature_cols = [c for c in self.numeric_cols if c != target_col][:6]
        if not feature_cols:
            return {"error": "No feature columns available"}

        X, y, used_cols = self._prepare_features(feature_cols, target_col)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        scaler = StandardScaler()
        X_train_s = scaler.fit_transform(X_train)
        X_test_s = scaler.transform(X_test)

        models = {
            "Linear Regression": LinearRegression(),
            "Ridge Regression": Ridge(alpha=1.0),
            "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
            "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42)
        }

        results = {}
        best_model_name = None
        best_r2 = -999

        for name, model in models.items():
            try:
                Xtr = X_train_s if "Regression" in name else X_train
                Xte = X_test_s if "Regression" in name else X_test
                model.fit(Xtr, y_train)
                y_pred = model.predict(Xte)
                r2 = r2_score(y_test, y_pred)
                rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                mae = mean_absolute_error(y_test, y_pred)
                results[name] = {"r2": round(float(r2), 4), "rmse": round(float(rmse), 4), "mae": round(float(mae), 4)}
                if r2 > best_r2:
                    best_r2 = r2
                    best_model_name = name
            except Exception as e:
                results[name] = {"error": str(e)}

        # Feature importance from best model
        importance = {}
        try:
            best_model = models[best_model_name]
            if hasattr(best_model, "feature_importances_"):
                imp = best_model.feature_importances_
                importance = {col: round(float(v), 4) for col, v in
                              sorted(zip(used_cols, imp), key=lambda x: x[1], reverse=True)}
            elif hasattr(best_model, "coef_"):
                coef = np.abs(best_model.coef_)
                importance = {col: round(float(v), 4) for col, v in
                              sorted(zip(used_cols, coef), key=lambda x: x[1], reverse=True)}
        except Exception:
            pass

        # Future predictions (next 5 values based on trend)
        predictions_sample = []
        try:
            best_model = models[best_model_name]
            sample_X = X_test_s[:5] if "Regression" in best_model_name else X_test[:5]
            preds = best_model.predict(sample_X)
            actuals = y_test[:5]
            predictions_sample = [{"actual": round(float(a), 2), "predicted": round(float(p), 2),
                                    "error_pct": round(abs(a-p)/max(abs(a),1)*100, 1)}
                                   for a, p in zip(actuals, preds)]
        except Exception:
            pass

        return {
            "task": "regression",
            "target": target_col,
            "features": used_cols,
            "train_size": len(X_train),
            "test_size": len(X_test),
            "model_results": results,
            "best_model": best_model_name,
            "best_r2": round(float(best_r2), 4),
            "feature_importance": importance,
            "sample_predictions": predictions_sample,
            "interpretation": f"Best model: {best_model_name} with R²={best_r2:.3f} — {'Good fit!' if best_r2>0.7 else 'Moderate fit' if best_r2>0.4 else 'Weak fit — try more features'}"
        }

    # ─── CLASSIFICATION ──────────────────────────────────
    def run_classification(self, target_col: str, feature_cols: list = None) -> dict:
        if feature_cols is None:
            feature_cols = [c for c in self.numeric_cols if c != target_col][:6]
        if not feature_cols:
            return {"error": "No feature columns"}

        df = self.df.copy()
        le_target = LabelEncoder()
        y = le_target.fit_transform(df[target_col].astype(str))

        X_list = []
        used_cols = []
        for col in feature_cols:
            if col == target_col:
                continue
            if df[col].dtype == object:
                le = LabelEncoder()
                X_list.append(le.fit_transform(df[col].astype(str)))
            else:
                X_list.append(df[col].fillna(df[col].median()).values)
            used_cols.append(col)

        X = np.column_stack(X_list)
        imp = SimpleImputer(strategy="mean")
        X = imp.fit_transform(X)

        n_classes = len(np.unique(y))
        if n_classes < 2:
            return {"error": "Need at least 2 classes"}
        if n_classes > 20:
            return {"error": "Too many classes (>20)"}

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y if len(y)>10 else None)

        models = {
            "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
            "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42)
        }

        results = {}
        best_model_name = None
        best_acc = 0

        for name, model in models.items():
            try:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                acc = accuracy_score(y_test, y_pred)
                results[name] = {"accuracy": round(float(acc), 4), "accuracy_pct": round(float(acc)*100, 1)}
                if acc > best_acc:
                    best_acc = acc
                    best_model_name = name
            except Exception as e:
                results[name] = {"error": str(e)}

        importance = {}
        try:
            best = models[best_model_name]
            if hasattr(best, "feature_importances_"):
                importance = {col: round(float(v), 4) for col, v in
                              sorted(zip(used_cols, best.feature_importances_), key=lambda x: x[1], reverse=True)}
        except Exception:
            pass

        return {
            "task": "classification",
            "target": target_col,
            "classes": le_target.classes_.tolist(),
            "n_classes": n_classes,
            "features": used_cols,
            "model_results": results,
            "best_model": best_model_name,
            "best_accuracy": round(float(best_acc)*100, 1),
            "feature_importance": importance,
            "interpretation": f"Best: {best_model_name} — {best_acc*100:.1f}% accuracy {'🟢 Excellent' if best_acc>0.9 else '🟡 Good' if best_acc>0.75 else '🔴 Needs improvement'}"
        }

    # ─── CLUSTERING ──────────────────────────────────────
    def run_clustering(self, n_clusters: int = None, feature_cols: list = None) -> dict:
        if feature_cols is None:
            feature_cols = self.numeric_cols[:5]
        if len(feature_cols) < 2:
            return {"error": "Need 2+ numeric columns for clustering"}

        df = self.df[feature_cols].copy()
        imp = SimpleImputer(strategy="mean")
        X = imp.fit_transform(df)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Auto find best k using elbow method
        if n_clusters is None:
            inertias = []
            k_range = range(2, min(9, len(X)//2))
            for k in k_range:
                km = KMeans(n_clusters=k, random_state=42, n_init=10)
                km.fit(X_scaled)
                inertias.append(km.inertia_)
            # Simple elbow detection
            diffs = [inertias[i]-inertias[i+1] for i in range(len(inertias)-1)]
            n_clusters = list(k_range)[diffs.index(max(diffs))+1] if diffs else 3

        km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = km.fit_predict(X_scaled)
        sil = silhouette_score(X_scaled, labels) if len(set(labels)) > 1 else 0

        # Cluster profiles
        df_with_clusters = self.df[feature_cols].copy()
        df_with_clusters["cluster"] = labels
        profiles = {}
        for i in range(n_clusters):
            cluster_data = df_with_clusters[df_with_clusters["cluster"] == i]
            profiles[f"Cluster {i+1}"] = {
                "size": int(len(cluster_data)),
                "pct": round(len(cluster_data)/len(df)*100, 1),
                "means": {col: round(float(cluster_data[col].mean()), 2) for col in feature_cols}
            }

        return {
            "task": "clustering",
            "n_clusters": n_clusters,
            "features": feature_cols,
            "silhouette_score": round(float(sil), 4),
            "quality": "Excellent" if sil > 0.7 else "Good" if sil > 0.5 else "Fair" if sil > 0.3 else "Poor",
            "cluster_profiles": profiles,
            "cluster_labels": labels.tolist()[:100],
            "interpretation": f"{n_clusters} clusters found. Silhouette={sil:.3f} — {'Well-separated clusters!' if sil>0.5 else 'Overlapping clusters'}"
        }

    # ─── FORECASTING (Time Series) ───────────────────────
    def run_forecasting(self, target_col: str, periods: int = 6) -> dict:
        if target_col not in self.numeric_cols:
            return {"error": f"'{target_col}' must be numeric"}

        series = self.df[target_col].dropna().values
        if len(series) < 6:
            return {"error": "Need at least 6 data points for forecasting"}

        n = len(series)
        X = np.arange(n).reshape(-1, 1)
        y = series

        # Fit linear trend
        model = LinearRegression()
        model.fit(X, y)
        trend_pred = model.predict(X)
        r2 = r2_score(y, trend_pred)

        # Forecast future
        future_X = np.arange(n, n + periods).reshape(-1, 1)
        future_pred = model.predict(future_X)

        # Moving average
        window = min(3, len(series)//2)
        ma = pd.Series(series).rolling(window=window).mean().fillna(method='bfill').values

        # Trend direction
        slope = float(model.coef_[0])
        trend_dir = "📈 Increasing" if slope > 0 else "📉 Decreasing" if slope < 0 else "➡️ Stable"

        return {
            "task": "forecasting",
            "target": target_col,
            "historical_values": [round(float(v), 2) for v in series[-20:]],
            "trend_line": [round(float(v), 2) for v in trend_pred[-20:]],
            "moving_average": [round(float(v), 2) for v in ma[-20:]],
            "forecast": [round(float(v), 2) for v in future_pred],
            "forecast_periods": periods,
            "trend_slope": round(slope, 4),
            "trend_direction": trend_dir,
            "r2_score": round(float(r2), 4),
            "interpretation": f"{trend_dir} trend. Slope={slope:.2f} per period. R²={r2:.3f}"
        }

    def get_ml_suggestions(self) -> dict:
        """Suggest what ML tasks are possible with this dataset"""
        suggestions = []
        if len(self.numeric_cols) >= 2:
            suggestions.append({"task": "regression", "description": f"Predict {self.numeric_cols[0]} using other columns", "target": self.numeric_cols[0]})
            suggestions.append({"task": "forecasting", "description": f"Forecast future values of {self.numeric_cols[0]}", "target": self.numeric_cols[0]})
        if self.categorical_cols:
            suggestions.append({"task": "classification", "description": f"Classify '{self.categorical_cols[0]}' from other features", "target": self.categorical_cols[0]})
        if len(self.numeric_cols) >= 2:
            suggestions.append({"task": "clustering", "description": f"Find natural groups in your data", "target": None})
        return {"suggestions": suggestions, "numeric_cols": self.numeric_cols, "categorical_cols": self.categorical_cols}
