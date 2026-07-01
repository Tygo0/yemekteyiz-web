# Architecture

## 1. High-Level Architecture

```
                 React Frontend
                        │
                  REST API (HTTPS)
                        │
                Flask Backend API
                        │
                  SQLAlchemy ORM
                        │
                  PostgreSQL Database
                        ▲
                        │
             REST API Requests Only
                        │
             AI Automation Pipeline
```

**Hard rule:** the automation service never performs SQL operations. All writes go
through backend API endpoints, which own validation and persistence.

## 2. Backend — Clean Architecture

```
backend/
  app/
    auth/          # login, JWT issuance, session
    contestants/
    weeks/
    episodes/
    dishes/
    scores/
    statistics/
    automation/     # endpoints the automation client calls
    models/         # SQLAlchemy models only — no business logic
    schemas/         # Marshmallow/Pydantic validation & serialization
    services/        # business logic lives here
    utils/
  tests/
```

Rules:
- Routes are thin — they parse input, call a service, return a response.
- Business logic lives only in `services/`.
- `models/` represent tables only, no queries beyond simple relationships.
- Every input is validated in `schemas/` before reaching a service.

## 3. Frontend

```
frontend/src/
  components/   # reusable UI
  pages/        # route-level views
  layouts/      # shared page shells (admin layout, public layout)
  services/     # Axios API clients
  hooks/        # custom hooks
  contexts/     # auth context, etc.
  router/       # React Router config, protected routes
  utils/
```

## 4. Database (ER overview)

```
Season 1──N Week 1──N Contestant 1──N Episode 1──N Dish
                                          │
                                          1──N Score
```

| Entity      | Key fields |
|-------------|------------|
| Season      | id, name, year |
| Week        | id, season_id (FK), week_number, air_date, youtube_url, winner_id (FK→Contestant), notes |
| Contestant  | id, week_id (FK), name, age, profession, city, biography, photo_url |
| Episode     | id, contestant_id (FK), broadcast_date, video_url |
| Dish        | id, episode_id (FK), name, category (enum: soup/appetizer/main/dessert/beverage) |
| Score       | id, episode_id (FK), judge_name, contestant_id (FK), value (1–10) |

Full ERD to be produced in Phase 2 (`docs/er-diagram.png` / dbdiagram.io source).

## 5. REST API Surface (v1)

```
Auth
  POST   /api/auth/login
  POST   /api/auth/logout
  GET    /api/auth/me

Contestants
  GET    /api/contestants
  POST   /api/contestants
  PUT    /api/contestants/{id}
  DELETE /api/contestants/{id}

Weeks
  GET    /api/weeks
  POST   /api/weeks
  PUT    /api/weeks/{id}
  DELETE /api/weeks/{id}

Episodes
  GET    /api/episodes
  POST   /api/episodes

Scores
  GET    /api/scores
  POST   /api/scores

Statistics
  GET    /api/statistics

Automation
  POST   /api/automation/import
  GET    /api/automation/status
  GET    /api/automation/logs
```

Auth endpoints and all admin-mutating endpoints (`POST/PUT/DELETE`) require a valid JWT
with the `admin` role. `GET` endpoints are public.

## 6. AI Automation Pipeline

```
automation/
  downloader/    # yt-dlp — detects & pulls new uploads
  extractor/      # ffmpeg — splits video into frames + audio
  ocr/             # PaddleOCR/EasyOCR on frames
  vision/          # Vision-LLM (Gemini / GPT-4.1) on frames
  speech/          # Whisper transcription + LLM extraction
  parser/          # fuses OCR + vision + speech into one structured object
  validator/       # rejects malformed/incomplete data before it's sent
  api_client/      # talks to backend exclusively over HTTPS/REST
  scheduler/       # cron-style polling of the YouTube channel
```

Pipeline stages: Discovery → Download → Media Extraction → Visual Understanding
(OCR + Vision LLM) → Speech Understanding (Whisper + LLM) → Data Fusion → Validation
→ Backend Integration (`POST /api/automation/import`).

Validation gate (non-negotiable): no duplicate contestants, week must exist, scores
in 1–10, exactly four contestants expected, all required fields present. Invalid
payloads are logged and never sent to the database.

## 7. Deployment

`docker-compose.yml` services: `frontend`, `backend`, `postgres`, `automation`.
Volumes: `database`, `logs`, `uploads`. All services share an internal bridge network;
only `frontend` and `backend` are exposed externally.

## 8. Engineering Principles

- API-first design.
- Separation of concerns; thin controllers, fat services.
- No duplicated business logic between backend and automation.
- Single responsibility per module.
- Automation is fully decoupled from the website — REST API only.
- Database schema is the single source of truth.
- Manual system ships completely before AI automation work begins.
