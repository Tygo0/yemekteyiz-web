# Development Roadmap

Tracks progress against the blueprint. Check items off as they land on `develop`.

## Phase 1 — Planning ✅ (in progress)
- [x] Repository created
- [x] Folder structure (backend / frontend / automation / docs)
- [x] README, ARCHITECTURE.md, ROADMAP.md
- [ ] Branch strategy set up (main / develop / feature/*)
- [ ] LICENSE decided

## Phase 2 — Database Design ✅
- [x] ER diagram finalized (`docs/er-diagram.md`)
- [x] SQLAlchemy models written (`backend/app/models/`)
- [x] Alembic migrations initialized and verified (upgrade + downgrade tested against a real DB)

## Phase 3 — Backend API ✅
- [x] JWT auth (login/logout/me)
- [x] CRUD: seasons, weeks, contestants, episodes, dishes, scores
- [x] Marshmallow schemas + validation (incl. 1-10 score range, dish category enum)
- [x] Statistics endpoint (weekly winners, avg score, highest score, most common dish, most successful contestant, avg weekly score, score distribution)
- [x] Automation endpoints stubbed (real pipeline is Phase 6)
- [x] Unit/integration tests — 16 passing, covering auth, full CRUD chain, validation rules, and statistics math

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
