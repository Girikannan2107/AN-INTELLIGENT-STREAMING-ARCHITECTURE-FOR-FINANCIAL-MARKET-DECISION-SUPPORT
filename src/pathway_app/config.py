"""
Configuration management using Pydantic Settings with environment variable support.
Implements Singleton pattern for global configuration access.
"""

from functools import lru_cache
from typing import List, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class KafkaSettings(BaseSettings):
    """Kafka configuration with validation."""
    bootstrap_servers: str = Field(default="localhost:9092", alias="KAFKA_BOOTSTRAP_SERVERS")
    group_id: str = Field(default="pathway-financial-group", alias="KAFKA_GROUP_ID")
    auto_offset_reset: str = "earliest"
    enable_auto_commit: bool = True
    
    @validator('bootstrap_servers')
    def validate_servers(cls, v: str) -> str:
        if not v or ':' not in v:
            raise ValueError("Invalid bootstrap_servers format. Expected 'host:port'")
        return v


class RedisSettings(BaseSettings):
    """Redis configuration."""
    url: str = Field(default="redis://localhost:6379", alias="REDIS_URL")
    password: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")
    db: int = Field(default=0, alias="REDIS_DB")
    socket_timeout: int = 5
    socket_connect_timeout: int = 5


class PathwaySettings(BaseSettings):
    """Pathway-specific settings."""
    runtime_typechecking: bool = Field(default=True, alias="PATHWAY_TYPECHECKING")
    monitoring_enabled: bool = Field(default=True, alias="PATHWAY_MONITORING")
    cache_dir: Optional[str] = Field(default="/tmp/pathway_cache", alias="PATHWAY_CACHE_DIR")


class APISettings(BaseSettings):
    """FastAPI configuration."""
    host: str = Field(default="0.0.0.0", alias="API_HOST")
    port: int = Field(default=8000, alias="API_PORT")
    reload: bool = Field(default=False, alias="API_RELOAD")
    workers: int = Field(default=1, alias="API_WORKERS")
    cors_origins: List[str] = Field(default=["*"], alias="CORS_ORIGINS")
    
    @validator('cors_origins', pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v


class Settings(BaseSettings):
    """
    Global application settings using Pydantic BaseSettings.
    Automatically loads from environment variables and .env file.
    """
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )
    
    app_name: str = "Intelligent Streaming Architecture"
    app_version: str = "0.1.0"
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # Nested configurations
    kafka: KafkaSettings = KafkaSettings()
    redis: RedisSettings = RedisSettings()
    pathway: PathwaySettings = PathwaySettings()
    api: APISettings = APISettings()
    
    # Financial data sources
    market_data_symbols: List[str] = Field(default=["AAPL", "GOOGL", "MSFT"], alias="MARKET_SYMBOLS")
    news_api_key: Optional[str] = Field(default=None, alias="NEWS_API_KEY")
    alpha_vantage_key: Optional[str] = Field(default=None, alias="ALPHA_VANTAGE_KEY")
    
    @validator('log_level')
    def validate_log_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"Invalid log level: {v}. Must be one of {allowed}")
        return v_upper


@lru_cache()
def get_settings() -> Settings:
    """
    Singleton pattern for settings.
    Cached to avoid reloading on every access.
    """
    return Settings()


# Global settings instance
settings = get_settings()
