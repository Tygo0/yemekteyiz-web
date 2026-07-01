# Phase 1 — Concepts & Reasoning (Meeting Prep Notes)

Written for someone who knows basic Python but hasn't done backend/web architecture
before. Goal: be able to explain *why* each decision was made, not just *what* was done.

---

## 1. Why three separate top-level folders (backend / frontend / automation)?

They are three **independent programs** that only communicate over HTTP (REST API
calls) — never by importing each other's code or sharing a database connection.

**Why this matters:** if the AI automation script could write to the database
directly, a bug in the AI (e.g. it misreads a score from a video frame) could corrupt
data with nobody checking it. By making automation talk *only* through the same API
the website's admin panel uses, every write — human or AI — passes through the same
validation. This is the #1 architectural rule of the project. If someone asks "why
not just let the automation write to Postgres directly, it'd be faster?" — the answer
is: speed isn't the goal, data integrity and a single source of truth are.

## 2. What is a REST API, in plain terms?

It's just an HTTP-based contract: the frontend (or automation) sends a request like
`POST /api/contestants` with JSON data, and the backend responds with JSON back.
"REST" is a naming/structure convention: URLs represent *things* (`/contestants`,
`/weeks`), and HTTP verbs represent *actions*:

| Verb   | Meaning         |
|--------|-----------------|
| GET    | read data       |
| POST   | create data     |
| PUT    | update data     |
| DELETE | remove data     |

You already know functions that take input and return output — think of each API
endpoint as a Python function that happens to be called over the network with JSON
instead of a direct function call.

## 3. Why split backend code into models / schemas / services / routes?

This is called a **layered (clean) architecture**. Each layer has exactly one job:

- **models/** — just describes the shape of data (a `Contestant` class mapped to a
  database table via SQLAlchemy). No logic here, ever.
- **schemas/** — validates incoming JSON before it's trusted (is `age` actually a
  number? is `name` present?). Think of it as `assert`-style checks, formalized.
- **services/** — where actual business logic/decisions live ("can you delete this
  contestant if they already have scores?").
- **routes/** (in `auth/`, `contestants/`, etc.) — the thin layer that receives an
  HTTP request, calls the right service function, and returns a response. It should
  contain almost no logic.

**Why bother, instead of writing everything in one function?** Because both the
website's admin panel *and* the AI automation need to "create a contestant." If that
logic lived inside a single Flask route, you'd end up copy-pasting it. By putting it
in `services/`, it's written once and reused. This is the standard "thin controller,
fat service" pattern used in most production backends, not something specific to
this project — worth knowing that term if it comes up.

## 4. What is an ORM, and why SQLAlchemy?

Normally you'd write raw SQL like `SELECT * FROM contestants WHERE week_id = 3`.
An ORM (Object-Relational Mapper) lets you write `Contestant.query.filter_by(week_id=3)`
instead — i.e., you interact with Python objects, and SQLAlchemy translates that into
SQL behind the scenes. Benefits: fewer SQL injection bugs, easier to reason about in
Python, and migrations (schema changes) are tracked in code via Alembic instead of
manually-run SQL scripts.

## 5. Why PostgreSQL specifically?

It's a relational database — good fit here because the data is inherently relational
(a Season *has* Weeks, a Week *has* Contestants, a Contestant *has* Episodes, etc. —
see the ER diagram in `ARCHITECTURE.md`). PostgreSQL is free, production-grade, and
has first-class support in the Python ecosystem via SQLAlchemy.

## 6. What is JWT authentication, in plain terms?

When an admin logs in, the backend doesn't keep a memory of "who's logged in" like
old-school sessions do. Instead, it hands back a signed token (JWT) containing the
user's identity. The frontend stores that token and sends it in every subsequent
request's headers. The backend can verify the token is genuine (it's cryptographically
signed) without needing to look anything up — this is why it scales well and is
standard for REST APIs. Visitors don't have a token; admin-only endpoints check for
one and reject the request if it's missing or invalid.

## 7. Why is the automation pipeline broken into so many small folders (downloader, ocr, vision, speech, parser, validator, api_client...)?

Same "single responsibility" idea as the backend. Each stage does exactly one thing
and hands its output to the next stage:

```
downloader → extractor → (ocr + vision) + (speech) → parser (fusion) → validator → api_client
```

Splitting it this way means each stage can be tested, debugged, or swapped out (e.g.
swap PaddleOCR for EasyOCR) without touching the others. It also mirrors the actual
pipeline stages described in the blueprint, so the code structure literally matches
the mental model of "what happens to a video, step by step."

## 8. Why does the validator stage exist as its own separate step?

Because AI extraction (OCR/Vision/Whisper) is inherently unreliable — models
hallucinate, misread numbers, etc. The validator is the last line of defense before
anything reaches the API: checks scores are 1–10, exactly four contestants, no
duplicates, all required fields present. If this fails, the data is logged but never
sent onward. This is what "invalid data must never reach the database" means in
practice.

## 9. Why Docker / Docker Compose?

Four different services (frontend, backend, postgres, automation) each have their own
dependencies (Node.js for frontend, Python+ffmpeg+whisper for automation, Postgres
itself). Docker Compose lets you spin all four up with one command
(`docker compose up`) in isolated containers, so "works on my machine" problems go
away and it deploys the same way in production as in development. We haven't built
this yet (Phase 8) but the folder structure was planned with it in mind from day one.

## 10. Why plan the Git branch strategy now, before writing real code?

`main` (always stable/deployable) and `develop` (integration branch) with feature
branches per functional area (`feature/backend`, `feature/ocr`, etc.) means multiple
people — or multiple *phases* of work — don't collide with each other, and `main`
never contains half-finished work. Deciding this now avoids messy merges later.

## 11. Why write README / ARCHITECTURE.md / ROADMAP.md before any real code?

Documentation-first isn't bureaucracy for its own sake — it's a forcing function to
think through the design *before* committing to code, and it's what makes phases 2–8
reviewable in daily meetings: anyone (including future-you) can check the roadmap and
know exactly what's done and what's next without reading the whole codebase.

## 12. Likely meeting questions & short answers

- **"Why doesn't automation write to the DB directly?"** → Single source of truth;
  every write, human or AI, goes through the same validated API.
- **"Why so many small folders instead of a few big files?"** → Single responsibility
  per module; easier to test, debug, and reuse logic across the admin panel and the
  automation client.
- **"What happens if the AI misreads a score?"** → The validator stage rejects
  malformed data before it ever reaches `POST /api/automation/import`.
- **"Why Postgres and not something like MongoDB?"** → Data is relational by nature
  (seasons → weeks → contestants → episodes → scores), so a relational DB is the
  natural fit.
- **"Why plan branches/docs before writing code?"** → Cheap to change a plan, expensive
  to refactor code; also gives the team (or graders/reviewers) a map of the project.
