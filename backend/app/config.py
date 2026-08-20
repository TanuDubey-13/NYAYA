import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "NYAYA"
    API_V1_STR: str = "/api/v1"
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # AI & Firebase (Keys have blank default to avoid throwing errors on direct local run)
    GEMINI_API_KEY: str = ""
    FIREBASE_PROJECT_ID: str = ""
    GOOGLE_APPLICATION_CREDENTIALS: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
