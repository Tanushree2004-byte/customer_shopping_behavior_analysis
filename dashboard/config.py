"""
Application configuration helpers.
"""

from dataclasses import dataclass
import os
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
    flask_env: str = os.getenv("FLASK_ENV", "development")
    secret_key: str = os.getenv("SECRET_KEY", "change-this-in-production")

    @property
    def db_url(self) -> str:
        """Build SQLAlchemy database URL from safe environment values."""
        return (
            f"postgresql+psycopg2://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()

