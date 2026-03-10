"""
session_store.py — Memory-efficient session storage
Stores DataFrame as compressed CSV bytes to reduce RAM usage
Auto-cleanup of old sessions to prevent memory overflow
"""
import pandas as pd
import io, gzip, time, threading
from typing import Optional, Dict

_store: Dict[str, dict] = {}
_lock  = threading.Lock()
SESSION_TTL = 7200  # 2 hours

# ── Compression helpers ────────────────────────────────
def _compress(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode='wb', compresslevel=6) as gz:
        df.to_csv(gz, index=False)
    return buf.getvalue()

def _decompress(data: bytes) -> pd.DataFrame:
    buf = io.BytesIO(data)
    with gzip.GzipFile(fileobj=buf, mode='rb') as gz:
        return pd.read_csv(gz)

# ── Public API ────────────────────────────────────────
def save_session(session_id: str, df: pd.DataFrame,
                 analysis: dict = None, charts: dict = None,
                 filename: str = "dataset"):
    _cleanup_old()
    with _lock:
        _store[session_id] = {
            "_df_bytes":  _compress(df),
            "analysis":   analysis or {},
            "charts":     charts or {},
            "filename":   filename,
            "shape":      list(df.shape),
            "columns":    df.columns.tolist(),
            "created_at": time.time(),
            "updated_at": time.time(),
        }


def get_session(session_id: str) -> Optional[dict]:
    with _lock:
        s = _store.get(session_id)
        if not s:
            return None
        if time.time() - s["created_at"] > SESSION_TTL:
            del _store[session_id]
            return None
        # Decompress df on-the-fly
        try:
            df = _decompress(s["_df_bytes"])
            # Restore session dict with live df (don't mutate store)
            return {**s, "df": df}
        except Exception:
            return None


def update_session(session_id: str, **kwargs):
    with _lock:
        if session_id not in _store:
            return
        if "df" in kwargs:
            # Re-compress updated df
            _store[session_id]["_df_bytes"] = _compress(kwargs.pop("df"))
            _store[session_id]["shape"]     = list(kwargs.get("shape", _store[session_id]["shape"]))
        _store[session_id].update(kwargs)
        _store[session_id]["updated_at"] = time.time()


def delete_session(session_id: str):
    with _lock:
        _store.pop(session_id, None)


def get_df(session_id: str) -> Optional[pd.DataFrame]:
    s = get_session(session_id)
    return s["df"] if s else None


def _cleanup_old():
    """Remove expired + oldest sessions if >20 stored"""
    with _lock:
        now = time.time()
        expired = [sid for sid, s in _store.items()
                   if now - s["created_at"] > SESSION_TTL]
        for sid in expired:
            del _store[sid]
        # If still too many, drop oldest
        if len(_store) > 20:
            oldest = sorted(_store.items(), key=lambda x: x[1]["created_at"])
            for sid, _ in oldest[:len(_store)-20]:
                del _store[sid]


def cleanup_old_sessions():
    _cleanup_old()


def apply_df_operation(session_id: str, operation: str, params: dict) -> dict:
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
                if method == "mean":      df[col] = df[col].fillna(df[col].mean())
                elif method == "median":  df[col] = df[col].fillna(df[col].median())
                elif method == "mode":    df[col] = df[col].fillna(df[col].mode()[0])
                elif method == "zero":    df[col] = df[col].fillna(0)
                elif method == "forward": df[col] = df[col].ffill()
                elif method == "backward":df[col] = df[col].bfill()
                else:                     df[col] = df[col].fillna(params.get("value", ""))
            else:
                df = df.fillna(0)

        elif operation == "drop_missing":
            col = params.get("column")
            df  = df.dropna(subset=[col]) if col else df.dropna()

        elif operation == "create_column":
            import numpy as np
            local_vars = {c: df[c] for c in df.columns}
            local_vars["np"] = np
            df[params["name"]] = eval(params["expression"], {"__builtins__": {}}, local_vars)

        elif operation == "filter_rows":
            df = df.query(params["expression"])

        elif operation == "sort":
            df = df.sort_values(params["column"], ascending=params.get("ascending", True)).reset_index(drop=True)

        elif operation == "normalize":
            import numpy as np
            col    = params.get("column")
            method = params.get("method", "minmax")
            if method == "minmax":
                df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
            elif method == "zscore":
                df[col] = (df[col] - df[col].mean()) / df[col].std()
            elif method == "log":
                df[col] = np.log1p(df[col])

        elif operation == "convert_type":
            col     = params.get("column")
            to_type = params.get("to_type")
            if to_type == "numeric":   df[col] = pd.to_numeric(df[col], errors="coerce")
            elif to_type == "string":  df[col] = df[col].astype(str)
            elif to_type == "datetime":df[col] = pd.to_datetime(df[col], errors="coerce")

        else:
            return {"success": False, "error": f"Unknown operation: {operation}"}

        update_session(session_id, df=df)
        return {
            "success": True, "operation": operation,
            "original_shape": list(original_shape),
            "new_shape": list(df.shape),
            "sample": df.head(5).fillna("").to_dict("records"),
            "columns": df.columns.tolist()
        }

    except Exception as e:
        return {"success": False, "error": str(e)}