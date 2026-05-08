"""
Application configuration helpers.
"""

from dataclasses import dataclass
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv


# Load environment variables from .env file if present.
load_dotenv()


@dataclass
class Settings:
    """Holds app settings loaded from environment variables."""

    db_user: str = os.getenv("DB_USER", "postgres")
    db_password: str = os.getenv("DB_PASSWORD", "postgres")
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: str = os.getenv("DB_PORT", "5432")
    db_name: str = os.getenv("DB_NAME", "consumer_db")
    db_table: str = os.getenv("DB_TABLE", "customer")
    database_url: str = os.getenv("DATABASE_URL", "")
    db_sslmode: str = os.getenv("DB_SSLMODE", "")
    flask_env: str = os.getenv("FLASK_ENV", "development")
    secret_key: str = os.getenv("SECRET_KEY", "change-this-in-production")

    @property
    def db_url(self) -> str:
        """
        Build SQLAlchemy DB URL.

        Priority:
        1) DATABASE_URL (recommended for cloud deployments like Vercel)
        2) DB_USER/DB_PASSWORD/DB_HOST/DB_PORT/DB_NAME parts
        """
        if self.database_url:
            # Some providers return postgres://; SQLAlchemy expects postgresql://.
            normalized = self.database_url.replace("postgres://", "postgresql://", 1)
            if "+psycopg2" not in normalized:
                normalized = normalized.replace("postgresql://", "postgresql+psycopg2://", 1)
            return normalized

        password = quote_plus(self.db_password)
        url = f"postgresql+psycopg2://{self.db_user}:{password}@{self.db_host}:{self.db_port}/{self.db_name}"

        if self.db_sslmode:
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}sslmode={self.db_sslmode}"

        return url


settings = Settings()

