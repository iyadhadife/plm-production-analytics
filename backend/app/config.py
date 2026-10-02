"""Application settings, read once at startup."""

import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BACKEND_DIR / ".env", override=True)


class Config:
    UPLOAD_DIR = BACKEND_DIR / "uploads"
    # Production build of the frontend (`npm run build` copied into backend/dist).
    STATIC_DIR = BACKEND_DIR / "dist"

    ALLOWED_EXTENSIONS = {
        "txt", "pdf", "png", "jpg", "jpeg", "gif", "doc", "docx", "webp", "xls", "xlsx", "csv",
    }

    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    GEMINI_MODEL = "gemini-2.5-flash"

    # The three source files every report is built from.
    MES_FILE = "MES_Extraction.xlsx"
    PLM_FILE = "PLM_DataSet.xlsx"
    ERP_FILE = "ERP_Equipes_Airplus.xlsx"
