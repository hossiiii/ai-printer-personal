"""
Configuration management for AI Printer
Handles environment variables and application settings
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    PROJECT_NAME: str = "AI Printer"
    VERSION: str = "2.0.0"
    DEVELOPMENT: bool = True
    LOG_LEVEL: str = "INFO"
    
    # API URLs
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"
    
    # Database Configuration
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "ai_printer"
    DB_PASSWORD: str = "ai_printer_password"
    DB_NAME: str = "ai_printer_db"
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    
    # Celery Configuration
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    WHISPER_MODEL: str = "whisper-1"
    
    # Google Drive Configuration
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/google/callback"
    
    # File Upload
    MAX_AUDIO_FILE_SIZE: int = 25 * 1024 * 1024  # 25MB for OpenAI Whisper
    ALLOWED_AUDIO_FORMATS: list = ["wav", "mp3", "m4a", "webm"]
    UPLOAD_DIR: str = "/tmp/uploads"
    
    # Document Processing
    SUPPORTED_DOCUMENT_TYPES: list = ["flyer", "announcement", "notice", "event", "meeting_minutes", "letter", "report"]
    
    # PDF Configuration
    PDF_OUTPUT_DIR: str = "/tmp/ai-printer"
    
    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_SECRET_KEY: str = "jwt-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Monitoring
    PROMETHEUS_ENABLED: bool = True
    PROMETHEUS_PORT: int = 9090
    
    class Config:
        env_file = ".env.development"
        case_sensitive = True

# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get application settings"""
    return settings
