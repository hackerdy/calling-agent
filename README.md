# AI Voice Agent Platform

A lightweight local-first AI voice agent platform with:
- **Python backend** (FastAPI + LiveKit Worker + SQLite)
- **React dashboard** (Vite + Tailwind CSS)
- **ElevenLabs TTS** + **OpenAI plugins** for the LiveKit agent

## Project Structure

```text
/backend
  /app
    config.py
    database.py
    main.py
    schemas.py
    store.py
  /tests
    test_api.py
  agent.py
  requirements.txt
  requirements-dev.txt
/frontend
  src/App.jsx
  src/index.css
  vite.config.js
.env.example
README.md
```

## 1) Prerequisites

- Python **3.11+**
- Node.js **18+**
- A LiveKit server (self-hosted or cloud)
- ElevenLabs API key
- OpenAI API key

## 2) Configure environment

Copy and edit environment values:

```bash
cp .env.example .env
```

Required values:
- `LIVEKIT_URL`
- `LIVEKIT_API_KEY`
- `LIVEKIT_API_SECRET`
- `OPENAI_API_KEY`
- `ELEVEN_API_KEY`

## 3) Run backend API

```bash
cd /home/runner/work/calling-agent/calling-agent
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements-dev.txt
uvicorn backend.app.main:app --reload
```

API runs on `http://localhost:8000`.

## 4) Run LiveKit voice worker

In another terminal:

```bash
cd /home/runner/work/calling-agent/calling-agent
source .venv/bin/activate
python backend/agent.py start
```

Behavior:
- Worker loads **latest settings from SQLite** on room entry.
- If availability is OFF, worker disconnects immediately.
- If availability is ON, worker starts with configured prompt + ElevenLabs voice.
- Agent exposes an `end_call` tool to hang up naturally.

## 5) Run frontend dashboard

```bash
cd /home/runner/work/calling-agent/calling-agent/frontend
npm install
npm run dev
```

Dashboard runs on `http://localhost:5173` and includes:
- Prompt + Voice ID configuration
- Global ON/OFF availability toggle
- Call history list (timestamp, duration, transcript, audio player when recording path is available)

## 6) SQLite schema

Tables are created automatically at startup:
- `settings` (single row): `personality_prompt`, `voice_id`, `is_available`
- `call_history`: `started_at`, `ended_at`, `duration_seconds`, `transcript_json`, `audio_file_path`

## 7) Run tests

```bash
cd /home/runner/work/calling-agent/calling-agent
source .venv/bin/activate
pytest backend/tests -q
```

## API Endpoints

- `GET /api/health`
- `GET /api/settings`
- `PUT /api/settings`
- `GET /api/call-history`
- `POST /api/call-history`
- `GET /api/call-history/{id}/audio`
