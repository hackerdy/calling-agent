from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .config import get_database_path


SETTINGS_SEED_ID = 1


def _connect(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    connection = _connect(get_database_path())
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_db() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                personality_prompt TEXT NOT NULL,
                voice_id TEXT NOT NULL,
                is_available INTEGER NOT NULL DEFAULT 1,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS call_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                started_at TEXT NOT NULL,
                ended_at TEXT,
                duration_seconds REAL NOT NULL DEFAULT 0,
                transcript_json TEXT NOT NULL,
                audio_file_path TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        existing = connection.execute("SELECT id FROM settings WHERE id = ?", (SETTINGS_SEED_ID,)).fetchone()
        if existing is None:
            connection.execute(
                """
                INSERT INTO settings (id, personality_prompt, voice_id, is_available)
                VALUES (?, ?, ?, ?)
                """,
                (
                    SETTINGS_SEED_ID,
                    "You are a helpful AI voice assistant.",
                    "default",
                    1,
                ),
            )
