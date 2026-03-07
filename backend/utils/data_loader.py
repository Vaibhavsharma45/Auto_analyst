"""
backend/utils/data_loader.py
Handles loading, cleaning, and saving datasets.
Supports CSV, TSV, Excel, JSON.
"""

import pandas as pd
import numpy as np
import os
import json
import io


SUPPORTED_EXTENSIONS = [".csv", ".tsv", ".xlsx", ".xls", ".json", ".txt"]


def load_dataframe(filepath: str) -> pd.DataFrame:
    """Load a file into a pandas DataFrame based on extension."""
    ext = os.path.splitext(filepath)[1].lower()

    if ext in [".csv", ".txt"]:
        # Try different separators
        for sep in [",", ";", "\t", "|"]:
            try:
                df = pd.read_csv(filepath, sep=sep, encoding="utf-8", on_bad_lines="skip")
                if df.shape[1] > 1:
                    return _clean_df(df)
            except Exception:
                pass
        return pd.read_csv(filepath, encoding="utf-8", on_bad_lines="skip")

    elif ext == ".tsv":
        return _clean_df(pd.read_csv(filepath, sep="\t", encoding="utf-8"))

    elif ext in [".xlsx", ".xls"]:
        return _clean_df(pd.read_excel(filepath))

    elif ext == ".json":
        with open(filepath, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            return _clean_df(pd.DataFrame(data))
        elif isinstance(data, dict):
            return _clean_df(pd.DataFrame([data]))
        else:
            raise ValueError("JSON must be array or object")

    else:
        raise ValueError(f"Unsupported file type: {ext}")


def load_from_string(text: str, sep: str = None) -> pd.DataFrame:
    """Load CSV/TSV from raw string."""
    if sep is None:
        # Detect separator
        first_line = text.split("\n")[0]
        if "\t" in first_line:
            sep = "\t"
        elif ";" in first_line:
            sep = ";"
        else:
            sep = ","

    df = pd.read_csv(io.StringIO(text), sep=sep, on_bad_lines="skip")
    return _clean_df(df)


def _clean_df(df: pd.DataFrame) -> pd.DataFrame:
    """Basic cleaning: strip whitespace, normalize column names."""
    # Clean column names
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace(r"[^\w\s]", "", regex=True)
        .str.replace(r"\s+", "_", regex=True)
        .str.lower()
    )

    # Strip string values
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace({"nan": np.nan, "None": np.nan, "": np.nan, "null": np.nan})

    # Try numeric conversion for object columns
    for col in df.select_dtypes(include="object").columns:
        try:
            converted = pd.to_numeric(df[col], errors="coerce")
            if converted.notna().sum() / len(df) > 0.8:
                df[col] = converted
        except Exception:
            pass

    return df


def df_to_csv_string(df: pd.DataFrame) -> str:
    return df.to_csv(index=False)


def df_to_excel_bytes(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Data", index=False)
        workbook = writer.book
        worksheet = writer.sheets["Data"]

        # Formatting
        header_fmt = workbook.add_format({
            "bold": True, "bg_color": "#161b22",
            "font_color": "#58a6ff", "border": 1,
            "border_color": "#30363d"
        })
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_fmt)
            worksheet.set_column(col_num, col_num, max(12, len(str(value)) + 4))

    buf.seek(0)
    return buf.read()


def get_sample_info(df: pd.DataFrame) -> dict:
    """Quick summary for validation after upload"""
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "sample": df.head(5).fillna("").to_dict("records")
    }

