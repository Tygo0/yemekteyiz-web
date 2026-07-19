# Yemekteyiz AI Automation Platform

Full-stack platform for the TV program **"Zuhal Topal'la Yemekteyiz"**, combining a manual
management system with an AI automation pipeline that watches new YouTube episodes and
extracts structured contestant/score/dish data automatically.

## Project Status

✅ Full manual management system (backend + frontend), locally runnable, released
as standalone executables (Linux + Windows, auto-built by CI on every tag — see
**Releases**). ✅ AI automation pipeline built mock-first per `docs/ARCHITECTURE.md`
(downloader/extractor/ocr/vision/speech/parser/validator/api_client/scheduler),
with the Gemini vision stage live-verified against the real API; the backend's
`POST /api/automation/import` is real (no longer stubbed). ✅ Containerized
deployment (`docker-compose.yml`: frontend + backend + Postgres) verified
end-to-end on real Docker — see `docs/DEPLOYMENT.md`. ⚠️ A fully-local
(no external API) vision engine was explored and works end-to-end, but real
testing found its extraction accuracy isn't reliable enough for production
use — see `docs/ROADMAP.md`'s Phase 9 for the honest writeup; Gemini remains
the default and recommended engine. See `docs/ROADMAP.md` for the full
phase-by-phase status.

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
| Automation | yt-dlp, FFmpeg, EasyOCR, Whisper, Gemini 2.5 Flash (vision) |
| Deployment | Docker, Docker Compose (frontend + backend + Postgres — see docs/DEPLOYMENT.md) |

## Repository Structure

```
yemekteyiz/
├── backend/       # Flask REST API (clean architecture: routes → services → models)
│                  #   + Dockerfile / docker-entrypoint.sh
├── frontend/      # React + Vite SPA + Dockerfile / nginx.conf (reverse-proxies /api)
├── automation/    # Independent AI pipeline (mock-first: every stage has a real + a mock implementation), talks to backend only via HTTP
├── docker-compose.yml   # frontend + backend + Postgres — see docs/DEPLOYMENT.md
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

Run the test suites:
```bash
cd backend && python3 -m pytest tests/ -v
cd frontend && npm test         # Vitest + React Testing Library
```

**AI automation pipeline** (optional — the manual system above works fully without it):
```bash
cd automation
pip install -r requirements.txt --break-system-packages
cp .env.example .env            # fill in GEMINI_API_KEY + backend admin credentials
python3 -m pytest tests/ -v     # mock-first: only test_gemini_smoke.py needs a real key

# cli.py runs as a module from the repo root (needs the backend running):
cd ..
python3 -m automation.cli --video-url <url> --week-id <id> --mock   # dry run, synthetic data
```
See `docs/ARCHITECTURE.md`'s "AI Automation Pipeline" section and
`docs/API_REFERENCE.md`'s Automation endpoints for the full picture.

**Local (no external API) vision engine** — an alternative to Gemini for
extracting contestants/dishes/scores, using a local Ollama model instead of a
hosted API call. Set `AUTOMATION_VISION_ENGINE=local` in `automation/.env`
(**default is `gemini`, and that's the recommended setting for any real use**);
no `GEMINI_API_KEY` is needed in local mode. Because a 7B local model is
unreliable at reading/writing Turkish directly, this engine never generates
Turkish text itself — see `automation/vision/local_vision.py` for the
index-based extraction scheme that guarantees any Turkish text in the result
is a verbatim OCR copy, not model output. Setup:
```bash
ollama pull qwen2.5:7b-instruct-q4_K_M   # or set OLLAMA_MODEL to another pulled model
ollama serve
python3 -m pytest automation/tests/test_local_vision_smoke.py -v   # skipped unless Ollama is reachable
```
**Known limitation, tested honestly against real footage** (full writeup in
`docs/ROADMAP.md`'s Phase 9): across several rounds of real-episode testing,
the pipeline engineering held up well (runs reliably end-to-end, correctly
refuses non-cooking footage instead of fabricating data, and the validator
caught every bad extraction before anything reached the database — zero bad
data in any real attempt). But the local 7B model's actual extraction
accuracy on genuinely noisy real broadcast OCR text did not reach a reliable
level — it can still confuse a dish name or a mid-sentence caption fragment
for a contestant's name. This looks like a real capability ceiling of a
small local model paired with an OCR pipeline, not a remaining bug to patch.
Treat this engine as a tested, documented feasibility exploration, not a
production-ready Gemini replacement.

## Deploying with Docker

A third option, for running this as a real service (Postgres instead of
SQLite, independently restartable containers) rather than developing or
running a single local copy:

```bash
cp .env.example .env    # then edit JWT_SECRET_KEY + POSTGRES_PASSWORD
docker compose up --build -d
```

Frontend at http://localhost:8080, backend API at http://localhost:5000.
Full guide, including how the pieces connect and production notes (secrets,
TLS, backups): **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)**.

## Engineering Principles

- API-first design; thin controllers, fat services.
- Automation is a fully independent client of the REST API — no direct SQL access.
- Database schema is the single source of truth.
- The manual management system must be 100% usable before AI automation is built.

## License

MIT — see `LICENSE`.
