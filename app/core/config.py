"""Configuration management for Identity Service."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database Configuration
    database_url: str = "postgresql://user:password@localhost:5432/identity_db"
    
    # JWT Configuration
    # Using HS256 with a symmetric secret key by default.
    # If you switch to RS256, jwt_secret_key must be a valid RSA private key in PEM format.
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    
    # Service Configuration
    service_name: str = "Identity Service"
    service_version: str = "1.0.0"
    debug: bool = False
    
    # Security
    password_min_length: int = 8
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
