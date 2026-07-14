from __future__ import annotations

import os
from pathlib import Path


def get_database_path() -> Path:
    raw = os.getenv("DATABASE_PATH", "backend/data/voice_agent.db")
    path = Path(raw)
    if not path.is_absolute():
        path = Path.cwd() / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def get_frontend_origin() -> str:
    return os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
