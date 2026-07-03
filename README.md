# Yemekteyiz AI Automation Platform

Full-stack platform for the TV program **"Zuhal Topal'la Yemekteyiz"**, combining a manual
management system with an AI automation pipeline that watches new YouTube episodes and
extracts structured contestant/score/dish data automatically.

## Project Status

🚧 v0.1.0 — Full manual management system (backend + frontend), locally runnable.
AI automation and containerized deployment are not built yet. See `docs/ROADMAP.md`.

## System Overview

Two independent responsibilities:

1. **Management System** — admins manually enter/edit weekly contestant data via a React
   frontend backed by a Flask REST API.
2. **AI Automation System** — a separate Python service that downloads new episodes,
   runs OCR/Whisper/Vision-LLM extraction, validates the result, and pushes it into the
   system **exclusively through the REST API** (never touches the database directly).

```
React Frontend → REST API (HTTPS) → Flask Backend → SQLAlchemy → PostgreSQL
                                          ▲
                                  REST API requests only
                                          │
                                AI Automation Pipeline
```

## Tech Stack

| Layer      | Technology |
|------------|------------|
| Backend    | Python 3.13+, Flask, SQLAlchemy, Flask-Migrate (Alembic), Pydantic/Marshmallow, JWT, Gunicorn |
| Frontend   | React, Vite, React Router, Axios, Material UI / Tailwind |
| Database   | PostgreSQL |
| Automation | yt-dlp, FFmpeg, PaddleOCR/EasyOCR, Whisper, Gemini/GPT-4.1 Vision, LangChain (optional) |
| Deployment | Docker, Docker Compose *(planned — not yet implemented, see docs/ROADMAP.md)* |

## Repository Structure

```
yemekteyiz/
├── backend/       # Flask REST API (clean architecture: routes → services → models)
├── frontend/      # React + Vite SPA
├── automation/    # Independent AI pipeline, talks to backend only via HTTP (not yet built — see docs/ROADMAP.md)
└── docs/          # Architecture, ER diagram, API spec, roadmap, local setup guide
```

See `docs/ARCHITECTURE.md` for the full design and `docs/ROADMAP.md` for the phased plan.

## Running It Locally

**Just want to run the app, not edit the code?** Download the standalone
executable from this repo's **Releases** page — no Python/Node install
required. See `HOW_TO_RUN.txt`.

**Want to edit/develop the code?** Full step-by-step guide (clean-room
verified, with troubleshooting): **[docs/RUNNING_LOCALLY.md](docs/RUNNING_LOCALLY.md)**

Quick version:

```bash
# Backend
cd backend
pip install -r requirements.txt --break-system-packages
cp .env.example .env
export FLASK_APP=wsgi.py
flask db upgrade
ADMIN_USERNAME=admin ADMIN_PASSWORD=changeme123 python3 seed.py
python3 wsgi.py                 # http://localhost:5000

# Frontend (new terminal)
cd frontend
npm install
cp .env.example .env
npm run dev                     # http://localhost:5173
```

Run the backend test suite:
```bash
cd backend
python3 -m pytest tests/ -v
```

## Engineering Principles

- API-first design; thin controllers, fat services.
- Automation is a fully independent client of the REST API — no direct SQL access.
- Database schema is the single source of truth.
- The manual management system must be 100% usable before AI automation is built.

## License

MIT — see `LICENSE`.
