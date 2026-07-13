from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="MODELFIT_",
        case_sensitive=False,
        extra="ignore",
    )

    env: str = "development"
    log_level: str = "INFO"

    api_host: str = "127.0.0.1"
    api_port: int = 8000
    api_base_url: str = "http://localhost:8000"

    database_url: str = "postgresql+asyncpg://modelfit:change-me@localhost:5432/modelfit"
    redis_url: str = "redis://localhost:6379/0"

    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "modelfit"
    minio_secret_key: str = "change-me-now"
    minio_secure: bool = False
    minio_bucket: str = "modelfit"

    mlflow_tracking_uri: str = "http://localhost:5000"

    gemma_license_accepted: bool = False
    default_candidate_models: str = "phi_4_mini,qwen3_8b"


@lru_cache
def get_settings() -> Settings:
    return Settings()
