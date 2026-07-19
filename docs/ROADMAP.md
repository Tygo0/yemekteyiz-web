# Development Roadmap

Tracks progress against the blueprint. Check items off as they land on `develop`.

## Phase 1 — Planning ✅
- [x] Repository created
- [x] Folder structure (backend / frontend / automation / docs)
- [x] README, ARCHITECTURE.md, ROADMAP.md
- [x] Branch strategy set up (main / develop / feature/*)
- [x] LICENSE decided (MIT)

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
but explicitly descoped at the time — no Docker was available to verify container
config, and shipping unverified Docker files in a release was judged too risky.
Phase 5 was rescoped to exactly what was asked: a release someone else can clone and
run locally, with documentation good enough that they don't need to ask questions.
Containerization returned as Phase 8 once it could actually be tested — see below.

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
  (week must exist, no duplicate contestants, scores 1–10, at least one
  contestant — relaxed from an originally-assumed exactly four once real
  data showed otherwise (week 215 has 5), see Phase 9 — all required
  fields, contestant/episode/score consistency)
- [x] Backend integration (`POST /api/automation/import`) — implemented in
  `backend/app/services/automation_service.py`, reuses existing
  contestant/episode/dish/score services (no duplicated business logic, no
  raw SQL from automation); real end-to-end test runs the full mock pipeline
  against a live Flask backend over real HTTP

Not yet done: real network run against an actual YouTube channel/video (only
the Gemini vision stage has been confirmed against a live API so far), and
the scheduler's video→week matching logic is left as an injected function
since it depends on the actual channel's naming conventions.

## Phase 7 — Testing ✅
- [x] Backend unit + integration tests — 35 passing (25 from Phases 1-5 + 10 for
  automation import/logging + regression coverage for the dish-category bug below)
- [x] Frontend tests — Vitest + React Testing Library set up (`frontend/npm test`),
  17 tests covering the core flows: auth (login success/failure, session
  restore/expiry, logout), route protection (redirect when unauthenticated),
  the Automation Logs page (status/log rendering, regression test that the
  removed trigger-import button stays gone), and the Contestants CRUD page
  (admin-only controls, create/delete). Found and fixed a real accessibility
  bug along the way — Contestants' form labels had no `htmlFor`/`id`
  association; the same pattern in Weeks/Episodes/Dishes/Scores is flagged
  as a follow-up.
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

## Phase 8 — Deployment ✅
- [x] docker-compose.yml (frontend, backend, postgres) — `automation` is
  deliberately excluded (needs a real `GEMINI_API_KEY` + heavy model
  downloads that don't fit a generic `up`; stays a separately-run process
  per the Phase 6 design). Frontend's nginx reverse-proxies `/api` to the
  backend container over Docker's internal DNS — same-origin, no CORS
  config needed, matching the same pattern `build_executable.py` already
  used for the standalone executable.
- [x] Production env config — root `.env.example` for Compose variable
  substitution (Postgres creds, `JWT_SECRET_KEY`, optional admin seed).
- [x] Final README + docs pass — `docs/DEPLOYMENT.md` (new), README's
  Project Status/Tech Stack/Repository Structure updated, `docs/ARCHITECTURE.md`'s
  Deployment section corrected to match what was actually built.

Verified end-to-end on real Docker (Docker Desktop + WSL2, not guessed):
built all three images, ran migrations against real Postgres, seeded an
admin, logged in and did a full create/read round-trip through the
frontend's nginx proxy, and confirmed data survives a container restart
(idempotent migrations + admin seed).

## Phase 9 — Local (API-free) Vision Engine ⚠️ built, not production-reliable

Explored whether the automation pipeline's Gemini dependency could be
replaced with a fully local stack (no external API calls at all), motivated
by a separate local video-summarization project (`video-understanding`) that
does everything — transcription, visual analysis, summarization — with local
models only. Built as a switchable alternative
(`AUTOMATION_VISION_ENGINE=gemini|local` in `automation/.env`; **default
stays `gemini`**), not a replacement — see `automation/vision/local_vision.py`
for the design rationale in full.

What was built, in `automation/vision/`:
- [x] `persistent_fragment_filter.py` — drops OCR fragments that are
  persistent on-screen noise (the show's own watermark/logo, present in
  nearly every frame) rather than a genuine contestant/dish/score graphic,
  using fuzzy frame-coverage matching since OCR renders the same watermark
  slightly differently almost every read.
- [x] `caption_filter.py` — drops sentence-like narration captions (day
  headers, judges' quoted commentary, prize-money announcements) via word
  count plus a small set of recurring host-narration word stems, folded to
  ASCII since EasyOCR doesn't always render Turkish diacritics correctly.
- [x] `frame_clustering.py` — groups consecutive frames sharing OCR content
  into one on-screen-graphic unit, instead of treating the whole episode's
  fragments as one flat pool or every frame in isolation.
- [x] `cluster_fusion.py` — merges per-cluster partial extractions into
  final contestant records, attributing dish/score-only clusters to
  whichever contestant was most recently established and merging
  fuzzy-matched re-mentions of the same name instead of duplicating.
- [x] Index-based extraction scheme: the local model (`qwen2.5:7b-instruct`)
  never generates Turkish text itself — every proper noun is resolved by
  the model picking an index into a numbered OCR-fragment list, with a
  plain Python lookup substituting the literal OCR string back in. This
  works around `qwen2.5:7b-instruct-q4_K_M` being unreliable at genuinely
  reading/writing Turkish (confirmed independently by the sibling
  `video-understanding` project's own testing).
- [x] `temperature=0` on every extraction call — without it, re-running the
  identical pipeline against the identical video produced wildly different
  contestant counts (6, then 2) purely from sampling randomness.
- [x] Stage/percentage progress reporting (`automation/progress.py`) added
  after a real run sat silent for ~2 hours with no way to tell whether it
  was progressing or stuck.
- [x] Relaxed the contestant-count validation from a hard-coded exactly-4
  (`automation/validator/rules.py`, `backend/app/schemas/automation_schema.py`)
  to a minimum of 1, after discovering real weeks don't always have 4 (week
  215 has 5) — this was a pre-existing latent assumption bug, not specific
  to the local engine, and applies to Gemini too.

**Real test results, in sequence** (same real broadcast footage each time,
each fix addressing the actual root cause of the previous failure):
1. First pass, one flat un-curated fragment list for the whole episode:
   **351** "contestants" instead of 4 — mostly OCR misreads of the show's
   watermark, each mistaken for a distinct person.
2. After watermark filtering: **7** — mostly long narration captions
   misread as contestants (one produced a hallucinated score of 200000,
   pulled from a caption about a cash prize).
3. After caption/narration filtering: **6**, then (after adding
   temperature=0) **2** on an identical re-run of the same video — proving
   the extraction had a real non-determinism problem independent of the
   filtering itself.
4. On a genuinely different full episode: **4** candidates (a plausible
   count, satisfying the relaxed validator by coincidence) but **all four
   were garbage** — a dish name (a dessert) mistaken for a person's name,
   plus mid-sentence fragments. Not a repeat of any prior failure category;
   a new one.

**Honest conclusion**: the surrounding pipeline engineering is sound — the
validator correctly protected data integrity on every single real attempt
across all of the above (zero bad data ever reached the database), and the
honesty/refusal design (an explicit `is_relevant`/`is_cooking_competition`
escape hatch, carried over from the Gemini engine) was independently
verified against real non-cooking footage ("Me at the zoo") and correctly
refused rather than fabricating data. But the underlying per-cluster
classification, even after several rounds of real, root-cause fixes, still
reliably confuses short OCR fragments (a dish name, a sentence fragment)
for a contestant's name on genuinely noisy real broadcast footage. This
looks like a real capability ceiling of pairing a 7B quantized local model
with an OCR-based preprocessing pipeline, not a remaining implementation
bug — Gemini's advantage here is reading the raw frames directly with a
categorically stronger multimodal model, not something a local 7B model
+ more filtering passes is likely to fully close.

**Status**: local engine is real, tested, switchable code — useful as a
documented feasibility exploration and a foundation for future work (a
larger local model, or fine-tuning OCR/vision specifically for this show's
graphics, were not attempted) — but Gemini remains the recommended default
for any actual production use.
