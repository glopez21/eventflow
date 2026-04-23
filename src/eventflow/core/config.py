"""Configuration for EventFlow."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    DATABASE_URL: str = "postgresql://eventflow:eventflow@localhost:5432/eventflow"
    REDIS_URL: str = "redis://localhost:6379/0"

    SECRET_KEY: str = "eventflow-secret-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    CORS_ORIGINS: str = "*"

    EVENT_BATCH_SIZE: int = 100
    EVENT_PROCESSING_TIMEOUT: int = 30

    WEBSOCKET_HEARTBEAT_INTERVAL: int = 30


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()