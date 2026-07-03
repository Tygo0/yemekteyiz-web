# Yemekteyiz AI Automation Platform

Full-stack platform for the TV program **"Zuhal Topal'la Yemekteyiz"**, combining a manual
management system with an AI automation pipeline that watches new YouTube episodes and
extracts structured contestant/score/dish data automatically.

## Project Status

🚧 Phase 4 complete — React frontend (public pages + admin controls). See `docs/ROADMAP.md`.

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
| Deployment | Docker, Docker Compose |

## Repository Structure

```
yemekteyiz/
├── backend/       # Flask REST API (clean architecture: routes → services → models)
├── frontend/      # React + Vite SPA
├── automation/    # Independent AI pipeline, talks to backend only via HTTP
├── docs/          # Architecture, ER diagram, API spec, roadmap
└── docker-compose.yml
```

See `docs/ARCHITECTURE.md` for the full design and `docs/ROADMAP.md` for the phased plan.

## Getting Started (Backend)

```bash
cd backend
pip install -r requirements.txt --break-system-packages   # or use a venv

cp ../.env.example .env   # then edit DATABASE_URL etc.
export FLASK_APP=wsgi.py

flask db upgrade                                    # create tables
ADMIN_USERNAME=admin ADMIN_PASSWORD=changeme python3 seed.py   # create first admin

flask run   # http://localhost:5000
```

Run the test suite:
```bash
cd backend
python3 -m pytest tests/ -v
```

Full Docker Compose setup (frontend + backend + postgres + automation) lands in
Phase 8 — see `docs/ROADMAP.md`.

## Getting Started (Frontend)

```bash
cd frontend
npm install
cp .env.example .env   # points VITE_API_BASE_URL at the backend

npm run dev       # http://localhost:5173
npm run build      # production build to dist/
npm run lint
```

## Engineering Principles

- API-first design; thin controllers, fat services.
- Automation is a fully independent client of the REST API — no direct SQL access.
- Database schema is the single source of truth.
- The manual management system must be 100% usable before AI automation is built.

## License

MIT — see `LICENSE`.
