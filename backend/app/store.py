from __future__ import annotations

import json
from typing import Any

from .database import SETTINGS_SEED_ID, get_connection
from .schemas import CallLog, CreateCallLog, Settings, TranscriptLine


def get_settings() -> Settings:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT personality_prompt, voice_id, is_available FROM settings WHERE id = ?",
            (SETTINGS_SEED_ID,),
        ).fetchone()

    if row is None:
        raise RuntimeError("Settings row not initialized")

    return Settings(
        personality_prompt=row["personality_prompt"],
        voice_id=row["voice_id"],
        is_available=bool(row["is_available"]),
    )


def update_settings(settings: Settings) -> Settings:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE settings
            SET personality_prompt = ?,
                voice_id = ?,
                is_available = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                settings.personality_prompt,
                settings.voice_id,
                1 if settings.is_available else 0,
                SETTINGS_SEED_ID,
            ),
        )

    return get_settings()


def _to_call_log(row: Any) -> CallLog:
    transcript_data = json.loads(row["transcript_json"])
    transcript = [TranscriptLine(**line) for line in transcript_data]

    audio_url = None
    if row["audio_file_path"]:
        audio_url = f"/api/call-history/{row['id']}/audio"

    return CallLog(
        id=row["id"],
        started_at=row["started_at"],
        ended_at=row["ended_at"],
        duration_seconds=row["duration_seconds"],
        transcript=transcript,
        audio_url=audio_url,
    )


def list_call_history() -> list[CallLog]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, started_at, ended_at, duration_seconds, transcript_json, audio_file_path
            FROM call_history
            ORDER BY started_at DESC
            """
        ).fetchall()

    return [_to_call_log(row) for row in rows]


def create_call_log(payload: CreateCallLog) -> CallLog:
    transcript_json = json.dumps([line.model_dump(mode="json") for line in payload.transcript])

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO call_history (started_at, ended_at, duration_seconds, transcript_json, audio_file_path)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                payload.started_at.isoformat(),
                payload.ended_at.isoformat() if payload.ended_at else None,
                payload.duration_seconds,
                transcript_json,
                payload.audio_file_path,
            ),
        )
        call_id = cursor.lastrowid
        row = connection.execute(
            """
            SELECT id, started_at, ended_at, duration_seconds, transcript_json, audio_file_path
            FROM call_history
            WHERE id = ?
            """,
            (call_id,),
        ).fetchone()

    if row is None:
        raise RuntimeError("Failed to create call log")

    return _to_call_log(row)


def get_call_audio_path(call_id: int) -> str | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT audio_file_path FROM call_history WHERE id = ?",
            (call_id,),
        ).fetchone()

    if row is None:
        return None
    return row["audio_file_path"]
