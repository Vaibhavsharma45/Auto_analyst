"""
backend/utils/db_connector.py
Database connection — MySQL, PostgreSQL, SQLite
"""
import pandas as pd
import os

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass


def test_connection(db_type: str, config: dict) -> dict:
    """Test if database connection works"""
    try:
        engine = _get_engine(db_type, config)
        with engine.connect() as conn:
            conn.execute(_get_test_query(db_type))
        return {"success": True, "message": "Connection successful!"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_tables(db_type: str, config: dict) -> dict:
    """List all tables in the database"""
    try:
        engine = _get_engine(db_type, config)
        if db_type == "sqlite":
            query = "SELECT name FROM sqlite_master WHERE type='table'"
        elif db_type == "mysql":
            query = "SHOW TABLES"
        else:
            query = "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
        df = pd.read_sql(query, engine)
        return {"success": True, "tables": df.iloc[:, 0].tolist()}
    except Exception as e:
        return {"success": False, "error": str(e)}


def load_table(db_type: str, config: dict, table: str, limit: int = 10000) -> pd.DataFrame:
    """Load a table into DataFrame"""
    engine = _get_engine(db_type, config)
    return pd.read_sql(f"SELECT * FROM {table} LIMIT {limit}", engine)


def run_query(db_type: str, config: dict, query: str) -> pd.DataFrame:
    """Run custom SQL query"""
    engine = _get_engine(db_type, config)
    return pd.read_sql(query, engine)


def _get_engine(db_type: str, config: dict):
    from sqlalchemy import create_engine, text
    if db_type == "sqlite":
        path = config.get("path", ":memory:")
        return create_engine(f"sqlite:///{path}")
    elif db_type == "mysql":
        h = config.get("host","localhost")
        p = config.get("port", 3306)
        u = config.get("user","root")
        pw = config.get("password","")
        db = config.get("database","")
        return create_engine(f"mysql+pymysql://{u}:{pw}@{h}:{p}/{db}")
    elif db_type == "postgresql":
        h = config.get("host","localhost")
        p = config.get("port", 5432)
        u = config.get("user","postgres")
        pw = config.get("password","")
        db = config.get("database","postgres")
        return create_engine(f"postgresql+psycopg2://{u}:{pw}@{h}:{p}/{db}")
    else:
        raise ValueError(f"Unsupported DB type: {db_type}")


def _get_test_query(db_type):
    from sqlalchemy import text
    return text("SELECT 1")
