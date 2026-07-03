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

## Phase 4 — React Frontend ✅
- [x] Dashboard (admin-only: quick stats, recent weeks)
- [x] Admin panel controls (add/edit/delete forms, shown only when authenticated — same pages as public view)
- [x] Public pages (Weeks, Contestants, Episodes, Dishes, Scores, Statistics)
- [x] Full edit capability on every entity (seasons, weeks incl. winner selection, contestants incl. bio/photo, episodes, dishes, scores) — not just create
- [x] JWT persisted client-side, auto-attached to requests, session restored on refresh
- [x] Design system: Fraunces/IBM Plex type pairing, çini-tile palette, ScorePaddle signature component
- [x] Verified against the real backend (login → create → edit → statistics, full round trip via curl; confirmed visitor reads reflect admin edits immediately)

## Phase 5 — Local-Runnable Release ✅
- [x] Website fully usable with zero AI involvement (achieved in Phase 4: full CRUD + edit on every entity)
- [x] Consolidated, clean-room-verified local setup guide (`docs/RUNNING_LOCALLY.md`) — caught and fixed 3 real bugs (bad default DB hostname, seed.py and wsgi.py both not loading .env, psycopg2 force-installed for the SQLite-only default path)
- [x] Standalone single-file executable distribution (`docs/BUILDING_RELEASE_EXECUTABLE.md`) — no Python/Node required to run, single process serves both API and frontend, auto-migrates DB and seeds an admin on first launch. Verified end-to-end in complete isolation (binary copied to an empty folder, zero source code present).
- [ ] Version tagged (`v0.1.0`) and published as a GitHub Release — final step, see instructions below

**Redefinition note:** originally scoped as "manual system complete," which Phase 4
already satisfied. Docker/Kubernetes/cloud deployment were considered for this phase
but explicitly descoped — this sandbox has no Docker available to verify container
config, and shipping unverified Docker files in a release was judged too risky.
Containerization may return as its own future phase once it can be tested for real.
Phase 5 is now scoped to exactly what was asked: a release someone else can clone and
run locally, with documentation good enough that they don't need to ask questions.

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
