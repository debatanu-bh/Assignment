import os
import warnings
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root; warn if missing so users know to copy .env.example
_env_path = Path(__file__).resolve().parent / ".env"
if not _env_path.exists():
    warnings.warn(
        "No .env file found. Falling back to defaults"
        "Copy .env.example to .env and update values for your environment",
        stacklevel=2,
    )
load_dotenv(_env_path)


class Config:
    """Central configuration management following Singleton pattern"""
    
    # Cloud configuration
    CLOUD_BASE_URL = os.getenv("CLOUD_BASE_URL")

    # Device configuration
    DEVICE_BASE_URL = os.getenv("DEVICE_BASE_URL")
    
    # Credentials
    USERNAME = os.getenv("IENSO_USERNAME")
    PASSWORD = os.getenv("IENSO_PASSWORD")
    
    # Test configuration
    RETRY_COUNT = int(os.getenv("RETRY_COUNT"))
    RETRY_DELAY = int(os.getenv("RETRY_DELAY"))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT"))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL")


config = Config()