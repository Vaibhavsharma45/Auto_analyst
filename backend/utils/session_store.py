"""
backend/utils/session_store.py
In-memory store for active analysis sessions.
Keeps DataFrames and analysis results in memory.
"""

import pandas as pd
from typing import Optional, Dict
import time
import threading

_store: Dict[str, dict] = {}
_lock = threading.Lock()
SESSION_TTL = 3600  # 1 hour


def save_session(session_id: str, df: pd.DataFrame, analysis: dict = None,
                 charts: dict = None, filename: str = "dataset"):
    with _lock:
        _store[session_id] = {
            "df": df,
            "analysis": analysis or {},
            "charts": charts or {},
            "filename": filename,
            "created_at": time.time(),
            "updated_at": time.time()
        }


def get_session(session_id: str) -> Optional[dict]:
    with _lock:
        session = _store.get(session_id)
        if session and time.time() - session["created_at"] < SESSION_TTL:
            return session
        elif session:
            del _store[session_id]
        return None


def update_session(session_id: str, **kwargs):
    with _lock:
        if session_id in _store:
            _store[session_id].update(kwargs)
            _store[session_id]["updated_at"] = time.time()


def delete_session(session_id: str):
    with _lock:
        _store.pop(session_id, None)


def cleanup_old_sessions():
    """Remove expired sessions"""
    with _lock:
        now = time.time()
        expired = [sid for sid, s in _store.items() if now - s["created_at"] > SESSION_TTL]
        for sid in expired:
            del _store[sid]


def get_df(session_id: str) -> Optional[pd.DataFrame]:
    session = get_session(session_id)
    return session["df"] if session else None


def apply_df_operation(session_id: str, operation: str, params: dict) -> dict:
    """
    Apply in-place operations to the dataframe:
    - drop_column, rename_column, drop_duplicates, fill_missing,
      drop_missing, create_column (expression), filter_rows, sort
    """
    session = get_session(session_id)
    if not session:
        return {"success": False, "error": "Session not found"}

    df = session["df"].copy()
    original_shape = df.shape

    try:
        if operation == "drop_column":
            col = params.get("column")
            df = df.drop(columns=[col])

        elif operation == "rename_column":
            df = df.rename(columns={params["old_name"]: params["new_name"]})

        elif operation == "drop_duplicates":
            df = df.drop_duplicates()

        elif operation == "fill_missing":
            col = params.get("column")
            method = params.get("method", "mean")
            if col:
                if method == "mean":
                    df[col] = df[col].fillna(df[col].mean())
                elif method == "median":
                    df[col] = df[col].fillna(df[col].median())
                elif method == "mode":
                    df[col] = df[col].fillna(df[col].mode()[0])
                elif method == "zero":
                    df[col] = df[col].fillna(0)
                elif method == "forward":
                    df[col] = df[col].ffill()
                elif method == "backward":
                    df[col] = df[col].bfill()
                else:
                    df[col] = df[col].fillna(params.get("value", ""))
            else:
                df = df.fillna(method=method) if method in ["ffill", "bfill"] else df.fillna(0)

        elif operation == "drop_missing":
            col = params.get("column")
            if col:
                df = df.dropna(subset=[col])
            else:
                df = df.dropna()

        elif operation == "create_column":
            new_col = params.get("name")
            expression = params.get("expression")
            # Safe eval with df columns as locals
            local_vars = {col: df[col] for col in df.columns}
            import numpy as np
            local_vars["np"] = np
            df[new_col] = eval(expression, {"__builtins__": {}}, local_vars)

        elif operation == "filter_rows":
            expression = params.get("expression")
            df = df.query(expression)

        elif operation == "sort":
            col = params.get("column")
            ascending = params.get("ascending", True)
            df = df.sort_values(col, ascending=ascending).reset_index(drop=True)

        elif operation == "convert_type":
            col = params.get("column")
            to_type = params.get("to_type")
            import pandas as pd
            if to_type == "numeric":
                df[col] = pd.to_numeric(df[col], errors="coerce")
            elif to_type == "string":
                df[col] = df[col].astype(str)
            elif to_type == "datetime":
                df[col] = pd.to_datetime(df[col], errors="coerce")

        elif operation == "normalize":
            col = params.get("column")
            method = params.get("method", "minmax")
            import numpy as np
            if method == "minmax":
                df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
            elif method == "zscore":
                df[col] = (df[col] - df[col].mean()) / df[col].std()
            elif method == "log":
                df[col] = np.log1p(df[col])

        else:
            return {"success": False, "error": f"Unknown operation: {operation}"}

        update_session(session_id, df=df)
        return {
            "success": True,
            "operation": operation,
            "original_shape": list(original_shape),
            "new_shape": list(df.shape),
            "sample": df.head(5).fillna("").to_dict("records"),
            "columns": df.columns.tolist()
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
