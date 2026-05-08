"""
Database access layer for PostgreSQL.
"""

from __future__ import annotations

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from dashboard.config import settings


def get_engine() -> Engine:
    """Create a reusable SQLAlchemy engine."""
    return create_engine(settings.db_url, pool_pre_ping=True)


def load_customer_data(engine: Engine) -> pd.DataFrame:
    """
    Load customer table from PostgreSQL.

    We load the full table once because dashboard filters and chart logic
    are easier and faster to manage in Pandas for this project size.
    """
    query = text(f"SELECT * FROM {settings.db_table}")
    return pd.read_sql(query, engine)


def check_connection(engine: Engine) -> tuple[bool, str]:
    """Quick health-check query for DB connectivity with debug-safe message."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True, ""
    except Exception as exc:
        return False, str(exc)

