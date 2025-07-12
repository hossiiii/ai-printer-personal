"""
Configuration management for AI Printer
Handles environment variables and application settings
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = ""
    
    # Google Drive Configuration
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    
    # Application Configuration
    DEVELOPMENT: bool = True
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_SECRET_KEY: str = "jwt-secret-key-change-in-production"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # File Upload Limits
    MAX_AUDIO_FILE_SIZE: int = 25 * 1024 * 1024  # 25MB for OpenAI Whisper
    ALLOWED_AUDIO_FORMATS: list = ["wav", "mp3", "m4a", "webm"]
    
    # Document Processing
    SUPPORTED_DOCUMENT_TYPES: list = ["flyer", "announcement", "notice", "event"]
    
    # PDF Configuration
    PDF_OUTPUT_DIR: str = "/tmp/ai-printer"
    
    # Google OAuth Configuration
    GOOGLE_REDIRECT_URI: str = "http://localhost:3000/auth/callback"
    
    class Config:
        env_file = ".env.development"
        case_sensitive = True

# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get application settings"""
    return settings
