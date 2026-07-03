# v0.1.0 — Manual Management System

First runnable release: a complete manual management system for tracking contestants,
weeks, episodes, dishes, and scores — no AI automation yet (that's a future phase).

## What's included

**Backend (Flask + PostgreSQL/SQLite + SQLAlchemy)**
- JWT authentication (admin login)
- Full CRUD on every entity: seasons, weeks, contestants, episodes, dishes, scores
- Statistics endpoint: weekly winners, average score, highest score ever, most common
  dish, most successful contestant, average weekly score, score distribution
- Validation at three layers: request schema, business-rule service checks, and
  database constraints (e.g. scores are enforced 1–10 at the DB level, not just in
  application code)
- 25 automated tests covering auth, the full entity CRUD chain, statistics math, and
  edge cases (duplicate weeks, mismatched contestant/episode scores, invalid winners)

**Frontend (React + Vite + Tailwind)**
- Public pages: Weeks, Contestants, Episodes, Dishes, Scores, Statistics
- Admin-only: Dashboard, Automation Logs (placeholder)
- Every entity is fully editable by a logged-in admin — visitors see the same pages
  read-only
- Custom design system (not a generic template): Fraunces/IBM Plex type pairing, a
  çini-tile-inspired color palette, and a "score paddle" component that echoes the
  show's actual judge-paddle scoring gimmick

**Documentation**
- `docs/RUNNING_LOCALLY.md` — step-by-step local setup guide, clean-room verified
  against a genuinely fresh checkout (this process caught and fixed two real bugs:
  a Docker-only database hostname in the example env file, and a seed script that
  was silently ignoring its own config file)
- `docs/ARCHITECTURE.md`, `docs/er-diagram.md` — system design and database schema
- `docs/ROADMAP.md` — phase-by-phase progress tracker
- `docs/PHASE1_CONCEPTS.md` through `PHASE5_CONCEPTS.md` — the reasoning behind every
  major decision, written for explaining the project to others

## Not included yet

- AI automation pipeline (video download, OCR, speech-to-text, vision-LLM extraction)
  — automation API endpoints exist but return honest "not implemented" placeholders
- Docker / containerized deployment — deliberately deferred rather than shipped
  unverified (see `docs/PHASE5_CONCEPTS.md` for why)

## Try it

See [`docs/RUNNING_LOCALLY.md`](docs/RUNNING_LOCALLY.md) — takes about 5 minutes,
no database installation required.
