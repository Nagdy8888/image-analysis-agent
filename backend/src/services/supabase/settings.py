"""Supabase/PostgreSQL settings. Load from project root .env."""
import os
from pathlib import Path

from dotenv import load_dotenv

_backend_dir = Path(__file__).resolve().parent.parent.parent
_project_root = _backend_dir.parent
load_dotenv(_project_root / ".env")

DATABASE_URI = os.getenv("DATABASE_URI", "").strip()
SUPABASE_ENABLED = bool(DATABASE_URI)
