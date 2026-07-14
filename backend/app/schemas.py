from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Settings(BaseModel):
    personality_prompt: str = Field(min_length=1)
    voice_id: str = Field(min_length=1)
    is_available: bool


class TranscriptLine(BaseModel):
    speaker: Literal["user", "agent"]
    text: str
    timestamp: datetime | None = None


class CallLog(BaseModel):
    id: int
    started_at: datetime
    ended_at: datetime | None = None
    duration_seconds: float
    transcript: list[TranscriptLine]
    audio_url: str | None = None


class CreateCallLog(BaseModel):
    started_at: datetime
    ended_at: datetime | None = None
    duration_seconds: float = 0
    transcript: list[TranscriptLine] = Field(default_factory=list)
    audio_file_path: str | None = None
