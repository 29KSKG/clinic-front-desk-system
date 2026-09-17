"""Application configuration loaded from environment variables."""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME = "ClinicDesk"
    VERSION = "1.0.0"
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./clinic.db")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "720"))
    FREE_CANCEL_HOURS = float(os.getenv("FREE_CANCEL_HOURS", "24"))
    LATE_CANCEL_FEE = float(os.getenv("LATE_CANCEL_FEE", "25"))
    CURRENCY = os.getenv("CURRENCY", "USD")
    MIN_DURATION_MIN = 15
    MAX_DURATION_MIN = 120
    MAX_PAGE_SIZE = 100


settings = Settings()
