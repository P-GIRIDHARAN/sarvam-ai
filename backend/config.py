import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / ".env")

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "sk_1yj1b7cl_r1dVNNBcBtb27ZNB00h1x1HL")
SARVAM_BASE_URL = os.getenv("SARVAM_BASE_URL", "https://api.sarvam.ai")
SARVAM_LLM_MODEL = os.getenv("SARVAM_LLM_MODEL", "sarvam-105b")

PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "127.0.0.1")

DB_PATH = ROOT_DIR / os.getenv("DATABASE_PATH", "docupulse.db")
UPLOAD_DIR = ROOT_DIR / os.getenv("UPLOAD_DIR", "uploads")
SAMPLES_DIR = ROOT_DIR / os.getenv("SAMPLES_DIR", "samples")

# Ensure directories exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
