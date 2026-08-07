import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "AI Clinical Decision Support System"
    APP_VERSION: str = "1.0.0"
    API_VERSION: str = "v1"
    DEBUG: bool = True
    
    # Security & API
    SECRET_KEY: str = "dev_secret_key_change_in_production"
    
    # Supabase Configuration
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    
    # AI & Upload Paths
    MODEL_PATH: str = "ai/models/xray_densenet121.pth"
    UPLOAD_DIRECTORY: str = "uploads"
    
    # CORS Configuration
    ALLOWED_ORIGINS: list[str] = ["*"]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Ensure upload directory exists
upload_path = Path(settings.UPLOAD_DIRECTORY)
upload_path.mkdir(parents=True, exist_ok=True)
