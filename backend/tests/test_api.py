from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.main import create_app


def test_settings_persist_roundtrip(monkeypatch, tmp_path):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_PATH", str(db_path))

    with TestClient(create_app()) as client:
        settings = client.get("/api/settings")
        assert settings.status_code == 200
        assert settings.json()["is_available"] is True

        updated = {
            "personality_prompt": "You are concise.",
            "voice_id": "voice_123",
            "is_available": False,
        }
        save = client.put("/api/settings", json=updated)
        assert save.status_code == 200
        assert save.json() == updated

        fetched = client.get("/api/settings")
        assert fetched.status_code == 200
        assert fetched.json() == updated


def test_call_history_returns_saved_transcript(monkeypatch, tmp_path):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_PATH", str(db_path))

    payload = {
        "started_at": "2026-01-01T00:00:00Z",
        "ended_at": "2026-01-01T00:00:30Z",
        "duration_seconds": 30,
        "transcript": [
            {"speaker": "user", "text": "Hello", "timestamp": "2026-01-01T00:00:02Z"},
            {"speaker": "agent", "text": "Hi there", "timestamp": "2026-01-01T00:00:03Z"},
        ],
    }

    with TestClient(create_app()) as client:
        created = client.post("/api/call-history", json=payload)
        assert created.status_code == 200
        assert created.json()["duration_seconds"] == 30

        history = client.get("/api/call-history")
        assert history.status_code == 200
        body = history.json()
        assert len(body) == 1
        assert body[0]["transcript"][0]["speaker"] == "user"
        assert body[0]["transcript"][1]["speaker"] == "agent"
