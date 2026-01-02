"""Application configuration using Pydantic Settings."""
import json
from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # MongoDB Configuration
    mongodb_uri: str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB connection URI"
    )
    mongodb_db_name: str = Field(
        default="asviglager",
        description="MongoDB database name"
    )
    
    # JWT Configuration
    jwt_secret_key: str = Field(
        ...,
        description="Secret key for JWT token generation"
    )
    jwt_algorithm: str = Field(
        default="HS256",
        description="JWT algorithm"
    )
    jwt_access_token_expire_minutes: int = Field(
        default=1440,  # 24 hours
        description="JWT access token expiration time in minutes"
    )
    jwt_refresh_token_expire_days: int = Field(
        default=30,  # 30 days
        description="JWT refresh token expiration time in days"
    )
    
    # API Configuration
    api_v1_prefix: str = Field(
        default="/api/v1",
        description="API v1 route prefix"
    )
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins"
    )
    
    # Environment
    environment: str = Field(
        default="development",
        description="Application environment"
    )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from JSON string if needed."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",")]
        return v


# Global settings instance
settings = Settings()
