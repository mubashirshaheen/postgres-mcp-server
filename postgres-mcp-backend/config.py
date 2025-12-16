"""Configuration settings for the PostgreSQL MCP App Backend."""
import os

from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / '.env'

load_dotenv(dotenv_path=ENV_PATH)
LOGGING_DB_URL = os.getenv("LOGGING_DB_URL", "")
region = os.getenv("AWS_REGION", "")
DB_URL = os.getenv("DB_URL", "")
PORT = os.getenv("PORT", 8765)
APP_NAME = os.getenv("APP_NAME", "TPS")
