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
- [x] Version tagged (`v0.1.0`, `v0.2.0`) and published as GitHub Releases, with
  `.github/workflows/release.yml` now building Linux + Windows executables on
  real CI runners (no cross-compiling) and attaching them automatically on
  every tag push

**Redefinition note:** originally scoped as "manual system complete," which Phase 4
already satisfied. Docker/Kubernetes/cloud deployment were considered for this phase
but explicitly descoped — this sandbox has no Docker available to verify container
config, and shipping unverified Docker files in a release was judged too risky.
Containerization may return as its own future phase once it can be tested for real.
Phase 5 is now scoped to exactly what was asked: a release someone else can clone and
run locally, with documentation good enough that they don't need to ask questions.

## Phase 6 — AI Automation ✅ (mock-first pipeline built, one stage live-verified)
Built mock-first per `docs/PHASE6_HANDOFF.md`: every stage has a clean
interface (`automation/*/base.py`) with a mock implementation (synthetic
data, no external deps) and a real one, wired together by `automation/pipeline.py`.
- [x] Video discovery (`automation/downloader/ytdlp_downloader.py`,
  `automation/scheduler/poller.py`) — real yt-dlp code written; not yet run
  against a live YouTube channel
- [x] Download + media extraction (`automation/extractor/ffmpeg_extractor.py`)
  — real ffmpeg code written; not yet run against a real video
- [x] OCR pipeline (`automation/ocr/easyocr_engine.py`, EasyOCR) — real code
  written; not yet run against real frames
- [x] Whisper speech pipeline (`automation/speech/whisper_engine.py`) — real
  code written; not yet run against real audio
- [x] Vision-LLM extraction (`automation/vision/gemini_vision.py`, **Gemini
  2.5 Flash**) — **live-verified**: a real API call against a synthetic test
  image correctly extracted contestant name, dish, and judge scores
  (`automation/scripts/verify_gemini.py`, `automation/tests/test_gemini_smoke.py`)
- [x] Data fusion + validation (`automation/parser/fusion.py`,
  `automation/validator/rules.py`) — enforces all 6 blueprint rules
  (week must exist, no duplicate contestants, scores 1–10, exactly four
  contestants, all required fields, contestant/episode/score consistency)
- [x] Backend integration (`POST /api/automation/import`) — implemented in
  `backend/app/services/automation_service.py`, reuses existing
  contestant/episode/dish/score services (no duplicated business logic, no
  raw SQL from automation); real end-to-end test runs the full mock pipeline
  against a live Flask backend over real HTTP

Not yet done: real network run against an actual YouTube channel/video (only
the Gemini vision stage has been confirmed against a live API so far), and
the scheduler's video→week matching logic is left as an injected function
since it depends on the actual channel's naming conventions.

## Phase 7 — Testing
- [x] Backend unit + integration tests — 35 passing (25 from Phases 1-5 + 10 for
  automation import/logging + regression coverage for the dish-category bug below)
- [ ] Frontend tests
- [x] Automation pipeline tests — 13 passing in `automation/tests/` (validator,
  fusion, full mock-pipeline-to-live-backend e2e, Gemini smoke test)
- [x] Manual QA pass (first round) — found and fixed real bugs the automated
  tests hadn't caught:
  - `POST /api/automation/import` had no persisted logging; `GET /automation/logs`
    always returned an empty list regardless of what happened — implemented real
    `AutomationImportLog` persistence.
  - The frontend's "Trigger Import" button always 400'd — a Phase 3-era leftover
    that POSTed with no body, fine for the old 501 stub but not for the now-real
    endpoint. Removed it; the Automation Logs page is read-only (status + real
    log history) since real imports are triggered by running the pipeline
    itself, not by clicking a button with no input.
  - `Dish.category` serialized as Python's enum repr (`"DishCategory.SOUP"`)
    instead of its plain value (`"soup"`) — a pre-existing bug in `DishSchema`,
    not caught before since no test checked the round-tripped value.
  - CSS `text-transform: uppercase` is locale-sensitive, and this site declares
    `<html lang="tr">` — labels containing "i" (e.g. "Highest score ever")
    rendered with a Turkish dotted İ for every visitor. Fixed on the Automation
    Logs, Dashboard, and Statistics pages.

## Phase 8 — Deployment
- [ ] docker-compose.yml (frontend, backend, postgres, automation)
- [ ] Production env config
- [ ] Final README + docs pass
