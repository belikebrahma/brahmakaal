"""
Configuration Management for Brahmakaal Enterprise API
Environment-based configuration with support for PostgreSQL, Redis, and security settings
"""

import os
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator
import secrets

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    app_name: str = "Brahmakaal Enterprise API"
    version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="production", env="ENVIRONMENT")
    
    # API Configuration
    api_v1_prefix: str = "/v1"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    
    # Security & JWT Configuration
    jwt_secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32), env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_refresh_token_expire_days: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    
    # CORS Configuration
    cors_origins: list[str] = Field(default=["*"], env="CORS_ORIGINS")
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: list[str] = Field(default=["*"], env="CORS_ALLOW_METHODS")
    cors_allow_headers: list[str] = Field(default=["*"], env="CORS_ALLOW_HEADERS")
    
    # Database Configuration (PostgreSQL)
    database_url: str = Field(
        default="postgres://avnadmin:AVNS_E8ad8bmRF1FxJVmOVS-@kaal-arisingpopli.c.aivencloud.com:13649/defaultdb?sslmode=require",
        env="DATABASE_URL"
    )
    database_pool_size: int = Field(default=20, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=30, env="DATABASE_MAX_OVERFLOW")
    database_pool_timeout: int = Field(default=30, env="DATABASE_POOL_TIMEOUT")
    database_pool_recycle: int = Field(default=3600, env="DATABASE_POOL_RECYCLE")
    
    # Redis Configuration (Caching)
    redis_enabled: bool = Field(default=False, env="REDIS_ENABLED")
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_pool_size: int = Field(default=10, env="REDIS_POOL_SIZE")
    redis_timeout: int = Field(default=5, env="REDIS_TIMEOUT")
    
    # Cache Settings
    cache_ttl_seconds: int = Field(default=3600, env="CACHE_TTL_SECONDS")  # 1 hour
    cache_prefix: str = Field(default="brahmakaal", env="CACHE_PREFIX")
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    rate_limit_storage: str = Field(default="memory", env="RATE_LIMIT_STORAGE")  # redis or memory
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="structured", env="LOG_FORMAT")  # structured or text
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # File Paths
    ephemeris_file_path: str = Field(default="de421.bsp", env="EPHEMERIS_FILE_PATH")
    data_directory: str = Field(default="data", env="DATA_DIRECTORY")
    
    # Performance Settings
    max_workers: int = Field(default=4, env="MAX_WORKERS")
    request_timeout: int = Field(default=30, env="REQUEST_TIMEOUT")
    
    # Email Configuration (for verification and notifications)
    email_enabled: bool = Field(default=False, env="EMAIL_ENABLED")
    smtp_host: Optional[str] = Field(default=None, env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    email_from: Optional[str] = Field(default=None, env="EMAIL_FROM")
    
    # Monitoring and Analytics
    analytics_enabled: bool = Field(default=True, env="ANALYTICS_ENABLED")
    metrics_enabled: bool = Field(default=True, env="METRICS_ENABLED")
    usage_tracking_enabled: bool = Field(default=True, env="USAGE_TRACKING_ENABLED")
    
    # API Keys and External Services
    webhook_secret: Optional[str] = Field(default=None, env="WEBHOOK_SECRET")
    
    # Subscription and Billing
    stripe_public_key: Optional[str] = Field(default=None, env="STRIPE_PUBLIC_KEY")
    stripe_secret_key: Optional[str] = Field(default=None, env="STRIPE_SECRET_KEY")
    stripe_webhook_secret: Optional[str] = Field(default=None, env="STRIPE_WEBHOOK_SECRET")
    
    @validator("cors_origins", "cors_allow_methods", "cors_allow_headers", pre=True)
    def parse_cors_lists(cls, v):
        """Parse comma-separated CORS values"""
        if isinstance(v, str):
            return [item.strip() for item in v.split(",")]
        return v
    
    @validator("database_url")
    def validate_database_url(cls, v):
        """Validate database URL format"""
        if not v.startswith(("postgresql://", "postgres://")):
            raise ValueError("Database URL must be a PostgreSQL connection string")
        return v
    
    @validator("redis_url")
    def validate_redis_url(cls, v):
        """Validate Redis URL format"""
        if not v.startswith("redis://"):
            raise ValueError("Redis URL must start with redis://")
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.environment.lower() in ["development", "dev", "local"]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment.lower() in ["production", "prod"]
    
    @property
    def database_config(self) -> dict:
        """Get database configuration for SQLAlchemy (asyncpg compatible)"""
        return {
            "pool_size": self.database_pool_size,
            "max_overflow": self.database_max_overflow,
            "pool_timeout": self.database_pool_timeout,
            "pool_recycle": self.database_pool_recycle,
            # Don't include echo or url here as they're passed separately
        }
    
    @property
    def redis_config(self) -> dict:
        """Get Redis configuration"""
        return {
            "url": self.redis_url,
            "max_connections": self.redis_pool_size,
            "socket_timeout": self.redis_timeout,
            "socket_connect_timeout": self.redis_timeout,
            "retry_on_timeout": True
        }
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings"""
    return Settings()

# Export commonly used settings
settings = get_settings()

def get_database_url() -> str:
    """Get database URL with fallback to production"""
    settings = get_settings()
    return settings.database_url 