import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Call Audit API"
    APP_DESCRIPTION: str = "FastAPI with MySQL for AI Call Audit System"
    APP_VERSION: str = "1.0.0"
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "call_audit_db")
    DB_PORT: int = int(os.getenv("DB_PORT", 3306))
    UPLOAD_DIR: str = os.path.join(os.getcwd(), "calls")

settings = Settings()