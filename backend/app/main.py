from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .config import get_frontend_origin
from .database import init_db
from .schemas import CallLog, CreateCallLog, Settings
from .store import create_call_log, get_call_audio_path, get_settings, list_call_history, update_settings


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI):
        init_db()
        yield

    app = FastAPI(title="AI Voice Agent Dashboard API", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[get_frontend_origin()],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/settings", response_model=Settings)
    def read_settings() -> Settings:
        return get_settings()

    @app.put("/api/settings", response_model=Settings)
    def save_settings(payload: Settings) -> Settings:
        return update_settings(payload)

    @app.get("/api/call-history", response_model=list[CallLog])
    def read_call_history() -> list[CallLog]:
        return list_call_history()

    @app.post("/api/call-history", response_model=CallLog)
    def save_call_log(payload: CreateCallLog) -> CallLog:
        return create_call_log(payload)

    @app.get("/api/call-history/{call_id}/audio")
    def read_call_audio(call_id: int) -> FileResponse:
        audio_path = get_call_audio_path(call_id)
        if audio_path is None:
            raise HTTPException(status_code=404, detail="Call not found")

        path = Path(audio_path)
        if not path.exists() or not path.is_file():
            raise HTTPException(status_code=404, detail="Audio file not found")

        return FileResponse(path=path, media_type="audio/wav", filename=path.name)

    return app


app = create_app()
