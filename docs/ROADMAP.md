# Development Roadmap

Tracks progress against the blueprint. Check items off as they land on `develop`.

## Phase 1 — Planning ✅ (in progress)
- [x] Repository created
- [x] Folder structure (backend / frontend / automation / docs)
- [x] README, ARCHITECTURE.md, ROADMAP.md
- [ ] Branch strategy set up (main / develop / feature/*)
- [ ] LICENSE decided

## Phase 2 — Database Design
- [ ] ER diagram finalized
- [ ] SQLAlchemy models written
- [ ] Alembic migrations initialized

## Phase 3 — Backend API
- [ ] JWT auth (login/logout/me)
- [ ] CRUD: contestants, weeks, episodes, dishes, scores
- [ ] Marshmallow/Pydantic schemas + validation
- [ ] Unit tests

## Phase 4 — React Frontend
- [ ] Dashboard
- [ ] Admin panel (protected routes)
- [ ] Public pages (contestants, results, recipes, statistics)

## Phase 5 — Manual System Complete
- [ ] Website fully usable with zero AI involvement

## Phase 6 — AI Automation
- [ ] Video discovery (yt-dlp polling)
- [ ] Download + media extraction (ffmpeg)
- [ ] OCR pipeline
- [ ] Whisper speech pipeline
- [ ] Vision-LLM extraction
- [ ] Data fusion + validation
- [ ] Backend integration (`/api/automation/import`)

## Phase 7 — Testing
- [ ] Backend unit + integration tests
- [ ] Frontend tests
- [ ] Automation pipeline tests
- [ ] Manual QA pass

## Phase 8 — Deployment
- [ ] docker-compose.yml (frontend, backend, postgres, automation)
- [ ] Production env config
- [ ] Final README + docs pass
