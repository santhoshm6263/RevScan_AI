"""Configuration management for RevScan AI."""
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Application settings."""
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_BASE_URL: str = "http://localhost:8000"

    MAX_STEPS: int = 20
    SCREENSHOT_DIR: str = str(BASE_DIR / "data" / "screenshots")
    UI_TREES_DIR: str = str(BASE_DIR / "data" / "ui_trees")
    KNOWLEDGE_DIR: str = str(BASE_DIR / "data" / "knowledge")
    SCAN_STATE_FILE: str = str(BASE_DIR / "data" / "scan_state.json")
    KNOWLEDGE_PACK_FILE: str = str(BASE_DIR / "data" / "knowledge" / "knowledge-pack.json")

    AI_PROVIDER: str = "mock"
    AI_API_KEY: str = ""
    AI_MODEL_NAME: str = "gemini-1.5-flash"

    ADB_DEVICE_ID: str = ""
    ADB_PATH: str = "adb"


settings = Settings()

# Ensure directories exist
os.makedirs(settings.SCREENSHOT_DIR, exist_ok=True)
os.makedirs(settings.UI_TREES_DIR, exist_ok=True)
os.makedirs(settings.KNOWLEDGE_DIR, exist_ok=True)
os.makedirs(os.path.dirname(settings.SCAN_STATE_FILE), exist_ok=True)
