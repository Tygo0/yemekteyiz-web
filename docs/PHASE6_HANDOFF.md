# Handoff to Claude Code — Phase 6 Start

> **Status:** this handoff has been acted on — see `docs/ROADMAP.md`'s Phase 6
> section for what's actually built. Kept as-is below as a historical record
> of the reasoning/decisions at the start of the phase, not a live status doc.

Written at the end of a long planning conversation in claude.ai, to carry context
into a Claude Code session pointed at this repo. Claude Code has full read access
to every file here (including `docs/PHASE*_CONCEPTS.md`, which are intentionally
gitignored but still present on disk) — read those first for the reasoning behind
everything in Phases 1–5 before touching Phase 6.

## Where things stand (Phases 1–5, all done)

- **Backend**: Flask + SQLAlchemy + Postgres/SQLite, full JWT auth, full CRUD +
  edit/delete on every entity (seasons, weeks, contestants, episodes, dishes,
  scores), a statistics endpoint, 25 passing tests. See `docs/ARCHITECTURE.md`
  and `docs/er-diagram.md`.
- **Frontend**: React + Vite + Tailwind, one unified set of pages (not separate
  public/admin trees) that mirrors the backend's real permission model —
  edit/delete controls just render conditionally on `isAuthenticated`.
- **Distribution**: two paths exist —
  1. `docs/RUNNING_LOCALLY.md` — normal dev setup (two terminals, SQLite default).
  2. `docs/BUILDING_RELEASE_EXECUTABLE.md` + `backend/launcher.py` +
     `backend/build_executable.py` — a single-file PyInstaller executable,
     already verified working on Linux; Windows `.exe` build was in progress
     on the user's machine (hit a `pip`/`python3` interpreter mismatch —
     multiple Python installs on Windows; fix was `python3 -m pip install
     pyinstaller` to guarantee the same interpreter installs it and runs it).
- **Release**: tag `v0.1.0` is pushed to `github.com/Tygo0/yemekteyiz-web`,
  `main` and `origin/main` are in sync. The actual GitHub Release page entry
  (not just the tag) may still need to be created via the GitHub UI —
  check before assuming it's done.
- **Automation endpoints exist but are stubbed** (`backend/app/automation/routes.py`
  returns 501/idle) — this is what Phase 6 replaces with real functionality.

## Why Phase 6 starts in Claude Code, not claude.ai

The claude.ai sandbox this was planned in has network access locked to package
registries only (pypi, npm, github) — it cannot reach YouTube, Gemini, OpenAI, or
run heavy local models. Everything in Phases 1–5 was built AND verified end-to-end
in that sandbox (real test runs, real curl checks, real isolated executable
tests) — Phase 6 is the first phase that structurally requires real network/API
access, which is why it's continuing here instead.

## Phase 6 decisions already made (don't re-litigate these — build on them)

- **OCR: EasyOCR** (not PaddleOCR) — user's explicit choice, lighter install.
- **Vision LLM: not yet decided** — user has no preference/experience here and
  explicitly delegated the choice. Recommendation: **Gemini API** (Gemini 2.x
  Flash or similar) over OpenAI — reasons to weigh when actually deciding:
  cost per image, whether the user already has a Google account (lower signup
  friction than OpenAI billing setup), and Gemini's native multi-frame/video
  understanding capabilities being a plausible fit for "watch an episode and
  extract scores." Verify current model names/pricing/capabilities via web
  search before committing — this recommendation was made without real
  research, purely as a reasonable starting default.
- **Build strategy: mock-first.** Build the full pipeline (folder structure per
  `docs/ARCHITECTURE.md`'s `automation/` layout: downloader, extractor, ocr,
  vision, speech, parser, validator, api_client, scheduler) with every stage
  real and testable EXCEPT the genuinely external ones (actual YouTube
  download, actual OCR/Vision/Whisper calls) — those get clean interfaces
  with mock/fake implementations first, so the pipeline's logic (data fusion,
  validation rules, backend API integration) can be fully tested with
  synthetic data before spending API credits or dealing with real video files.
  Swap in real implementations behind the same interface once mocks prove the
  pipeline logic is correct.

## Validation rules already specified (from the original blueprint, Phase 3's
score/dish schemas, and `docs/ARCHITECTURE.md`) — the automation validator
stage must enforce all of these before ever calling `POST /api/automation/import`:
- No duplicate contestants per week
- Week must already exist (created by an admin, matching "manual system before
  automation" principle)
- Scores between 1 and 10 (matches the DB CHECK constraint and Marshmallow
  schema in `backend/app/schemas/score_schema.py`)
- Exactly four contestants expected per episode/week
- All required fields present
- A score's `contestant_id` must match the episode's `contestant_id`
  (see `backend/app/services/score_service.py` — the backend already enforces
  this; automation's own validator should catch it earlier with a clearer
  error, not rely solely on the backend rejecting it)

## First steps for Claude Code

1. Read `docs/ARCHITECTURE.md`'s "AI Automation Architecture" section and the
   existing (empty) `automation/` folder structure.
2. Confirm real network/API access works: can it actually reach pypi for
   `yt-dlp`/`easyocr`/`openai-whisper` installs, and whatever Vision API gets
   chosen?
3. Decide the Vision LLM for real (see recommendation above, but verify with
   current research rather than trusting a claude.ai-sandbox guess).
4. Build the mock-first pipeline skeleton, stage by stage, matching the
   blueprint's Stage 1–8 breakdown in `docs/ARCHITECTURE.md`.
5. Get `automation/api_client/` talking to the real backend
   (`POST /api/automation/import`) with synthetic data first — this is fully
   testable without any external AI service, same as everything in Phases 1–5.
