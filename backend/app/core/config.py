import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env")

API_V1_PREFIX = "/api/v1"

PROJECT_NAME = "TruthCams AI"
PROJECT_DESCRIPTION = "AI-powered information verification platform"
PROJECT_VERSION = "1.0.0"

FRONTEND_ORIGIN = "http://localhost:5173"

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is not configured.")

JWT_EXPIRE_MINUTES = int(
    os.getenv("JWT_EXPIRE_MINUTES", "30")
)

JWT_ALGORITHM = "HS256"