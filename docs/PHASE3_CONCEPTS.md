# Phase 3 — Concepts & Reasoning (Meeting Prep Notes)

## 1. Why does almost every route look nearly identical (load schema → call service → jsonify)?

That's intentional, not repetition-for-its-own-sake. It's the "thin controller" pattern
from Phase 1: a route's only job is translating HTTP ↔ Python. If someone asks "why
does `create_week` look basically like `create_contestant`?" — the answer is that
consistency here means anyone on the team can predict what a route does without
reading it closely, and all the actual decisions (can this be created? does the
parent exist? is this a duplicate?) live in one place: the service function.

## 2. Why validate the same thing twice — in the Marshmallow schema *and* in the service?

They check different things. The **schema** checks shape: is `value` an integer
between 1 and 10, is `name` a non-empty string, is `category` one of five known
strings. It has no idea what's in the database. The **service** checks state: does
the week this contestant claims to belong to actually exist, is this week number
already taken for this season, does the winner being set actually belong to this
week. A schema literally cannot answer "does this season exist" — that requires a
database query, which is a service's job, not a schema's.

## 3. Why does `POST /api/scores` reject a request where the schema itself is perfectly valid (e.g. `value: 8` is in range) but the API still returns 400?

This is the score/episode/contestant mismatch check: a score is always *for* the
contestant that a specific episode belongs to (episode → one contestant's cooking
session). If a request says "episode 5, but score contestant 7" and episode 5 belongs
to contestant 3, that's internally inconsistent data — schema validation can't catch
this because it doesn't know about relationships between IDs, only about the shape of
each field individually. This is a good concrete example to have ready if someone
asks "why isn't Marshmallow enough on its own?"

## 4. Why is `PUT /api/weeks/{id}` a separate schema (`WeekUpdateSchema`) from `POST /api/weeks` (`WeekSchema`)?

On create, `season_id` and `week_number` are required — a week can't exist without
them. On update, you might only want to change `notes`, so *nothing* should be
required. Using one schema with `partial=True` for updates would technically work,
but a dedicated update schema documents intent clearly and stops someone accidentally
making `season_id` re-assignable through a PUT (which should probably never happen —
you don't want to be able to move a week to a different season by editing it).

## 5. Why are GET endpoints public but POST/PUT/DELETE require a JWT?

This matches the user roles from Phase 1 exactly: Visitors can view everything,
Admins can create/edit/delete. `@jwt_required()` is a decorator from
Flask-JWT-Extended that runs before the route function — if there's no valid token in
the `Authorization: Bearer <token>` header, the request never reaches the route logic
at all and gets a 401 automatically.

## 6. Why is the automation API stubbed out now instead of built for real?

Straight from the blueprint's engineering principles: "build the manual management
system completely before implementing AI automation." The endpoints exist now
(`/api/automation/import`, `/status`, `/logs`) so the REST API surface is complete and
the frontend (Phase 4) can be built against real routes — but they return `501 Not
Implemented` / placeholder data until Phase 6, where the actual pipeline gets wired in.

## 7. How were these actually verified, not just written?

All 16 tests run against a real (in-memory SQLite) database through the actual HTTP
layer — `client.post("/api/scores", json={...})` — not by calling service functions
directly. That matters because it proves the whole path works: routing → schema
validation → service logic → database → serialized response. Specific things proven,
not assumed:
- A duplicate week number for the same season is rejected (409).
- A week pointing at a season that doesn't exist is rejected (404).
- A score value outside 1–10 is rejected by the schema before it reaches the DB (400).
- A score naming a contestant that doesn't match the episode's actual contestant is
  rejected (400) — this one caught a real gap in relying on schema validation alone.
- Deleting a week cascades and actually removes its contestants (not just the week row).
- The statistics math is correct against known input (average score, most successful
  contestant by average, weekly winners, score histogram) — computed by hand and
  asserted, not eyeballed.
- One real bug was caught by testing rather than assumed away: `score_distribution`
  building a dict with **int** keys works fine in Python, but Flask's `jsonify()`
  converts all dict keys to strings — so `stats["score_distribution"][10]` would
  silently return `KeyError` once JSON-encoded, even though the Python code looked
  correct. The test caught it before it became a frontend bug in Phase 4.

## 8. Likely meeting questions & short answers

- **"How do you know the API actually works, not just that it doesn't crash?"** →
  16 tests hit real HTTP endpoints against a real database and assert on actual
  values (e.g. average score is 7.75, not just "status 200").
- **"What stops a bad admin request from corrupting data?"** → Two layers: schema
  validation for shape/type (Marshmallow), service-level checks for relationships
  and business rules (does the parent exist, is this a duplicate, does this ID
  actually belong to that other ID).
- **"Why separate schemas for create vs. update?"** → Different fields are required
  in each case, and it prevents fields that shouldn't be editable (like reassigning
  a week to a different season) from silently becoming editable through PUT.
- **"Is the automation API real yet?"** → The routes exist and return proper JSON,
  but the actual AI pipeline behind them is Phase 6 — right now they're placeholders
  by design, matching the blueprint's phased approach.
