import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./cropshield.db"
    SECRET_KEY: str = "cropshield_phase1_super_secret_jwt_key_local_dev_123456789"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    # Plant Information APIs: Perenual (Primary) & Trefle (Legacy/Alternative)
    PERENUAL_API_KEY: str = ""
    PERENUAL_API_BASE_URL: str = "https://perenual.com/api"
    PLANT_API_KEY: str = ""
    PLANT_API_BASE_URL: str = "https://trefle.io/api/v1"

    # AI Conversational Assistant Settings: Google Gemini
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.5-flash"
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Weather Advisory API Settings
    WEATHER_API_KEY: str = ""
    WEATHER_API_BASE_URL: str = "https://api.openweathermap.org/data/2.5"
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]

    @property
    def effective_database_url(self) -> str:
        # If running in serverless environment (e.g. Vercel) and using default SQLite, use writable /tmp
        if (os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")) and self.DATABASE_URL == "sqlite:///./cropshield.db":
            return "sqlite:////tmp/cropshield.db"
        return self.DATABASE_URL

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
