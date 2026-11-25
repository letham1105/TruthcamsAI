import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
AI_SERVICE_ROOT = PROJECT_ROOT / "ai_service"
MODELS_DIR = AI_SERVICE_ROOT / "models"
QWEN_MODEL_DIR = MODELS_DIR / "qwen"
VELECTRA_MODEL_DIR = MODELS_DIR / "velectra"

load_dotenv(PROJECT_ROOT / ".env")

APP_NAME = "Truthcams AI"
APP_VERSION = "0.1.0"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "25"))
GOOGLE_NEWS_MAX_RESULTS = int(os.getenv("GOOGLE_NEWS_MAX_RESULTS", "10"))
BM25_TOP_K = int(os.getenv("BM25_TOP_K", "5"))
USER_AGENT = os.getenv(
    "USER_AGENT",
    "Mozilla/5.0 (compatible; TruthcamsAI/0.1; research retrieval)"
)

OCR_LANGUAGE = os.getenv("OCR_LANGUAGE", "vie+eng")
OCR_CONFIG = os.getenv("OCR_CONFIG", "--psm 6")

QWEN_MODEL_NAME = os.getenv("QWEN_MODEL_NAME", "Qwen/Qwen3-8B")
LOAD_QWEN = os.getenv("LOAD_QWEN", "false").lower() == "true"

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "")
