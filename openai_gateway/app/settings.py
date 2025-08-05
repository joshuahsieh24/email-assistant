"""Application settings and configuration."""

from typing import Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    app_name: str = "OpenAI Gateway"
    app_version: str = "0.1.0"
    debug: bool = Field(default=False, env="DEBUG")
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")

    # OpenAI Configuration
    openai_base_url: str = Field(default="https://api.openai.com", env="OPENAI_BASE_URL")
    openai_api_key: str = Field(env="OPENAI_API_KEY")

    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    redis_ttl_hours: int = Field(default=24, env="REDIS_TTL_HOURS")

    # JWT Configuration
    jwt_secret_key: str = Field(default="default-secret-key", env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=60, env="JWT_EXPIRE_MINUTES")

    # Rate Limiting
    rate_limit_requests: int = Field(default=60, env="RATE_LIMIT_REQUESTS")
    rate_limit_window_seconds: int = Field(default=60, env="RATE_LIMIT_WINDOW_SECONDS")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")

    # Presidio Configuration
    presidio_language: str = Field(default="en", env="PRESIDIO_LANGUAGE")
    presidio_supported_languages: list[str] = Field(
        default=["en"], env="PRESIDIO_SUPPORTED_LANGUAGES"
    )

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings() 