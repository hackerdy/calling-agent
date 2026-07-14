from __future__ import annotations

import asyncio
import os
from datetime import UTC, datetime

from dotenv import load_dotenv

from app.database import init_db
from app.schemas import CreateCallLog, TranscriptLine
from app.store import create_call_log, get_settings

load_dotenv()


try:
    from livekit.agents import (
        Agent,
        AgentSession,
        JobContext,
        WorkerOptions,
        RunContext,
        cli,
        function_tool,
    )
    from livekit.plugins import elevenlabs, openai
except Exception as exc:  # pragma: no cover - import guard for environments without livekit deps
    raise RuntimeError(
        "LiveKit dependencies are required. Install backend/requirements.txt before running agent.py"
    ) from exc


@function_tool
async def end_call(context: RunContext) -> str:
    """End the current call when the conversation is naturally complete."""

    await context.session.say("Thanks for calling. Goodbye.")
    await context.room.disconnect()
    return "Call ended"


class VoiceAssistantAgent(Agent):
    def __init__(self, system_prompt: str, voice_id: str):
        super().__init__(
            instructions=system_prompt,
            tools=[end_call],
            stt=openai.STT(),
            llm=openai.LLM(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini")),
            tts=elevenlabs.TTS(
                api_key=os.environ["ELEVEN_API_KEY"],
                voice_id=voice_id,
            ),
        )


async def entrypoint(ctx: JobContext) -> None:
    init_db()
    settings = get_settings()

    await ctx.connect()

    if not settings.is_available:
        await ctx.room.disconnect()
        return

    transcript: list[TranscriptLine] = []
    started_at = datetime.now(UTC)

    session = AgentSession(vad=openai.VAD())

    @session.on("user_speech_committed")
    def on_user_speech(text: str) -> None:
        transcript.append(TranscriptLine(speaker="user", text=text, timestamp=datetime.now(UTC)))

    @session.on("agent_speech_committed")
    def on_agent_speech(text: str) -> None:
        transcript.append(TranscriptLine(speaker="agent", text=text, timestamp=datetime.now(UTC)))

    agent = VoiceAssistantAgent(
        system_prompt=settings.personality_prompt,
        voice_id=settings.voice_id,
    )

    await session.start(room=ctx.room, agent=agent)
    await session.generate_reply(instructions="Greet the caller and ask how you can help.")

    try:
        await asyncio.Event().wait()
    finally:
        ended_at = datetime.now(UTC)
        create_call_log(
            CreateCallLog(
                started_at=started_at,
                ended_at=ended_at,
                duration_seconds=(ended_at - started_at).total_seconds(),
                transcript=transcript,
                audio_file_path=None,
            )
        )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
