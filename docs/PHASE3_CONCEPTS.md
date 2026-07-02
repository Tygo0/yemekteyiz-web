# Phase 3 — Concepts & Reasoning (Meeting Prep Notes)

## 1. Why JWT instead of traditional sessions?

A traditional session stores "who's logged in" in server memory or a session table,
and the browser holds a cookie that references it. JWT flips this: the server signs a
token containing the admin's identity and hands it to the client. The client sends
that token on every request; the server verifies the signature and trusts the
contents — no database lookup needed to check "is this session valid." This is why
JWT is the standard choice for REST APIs, especially ones that might later be called
by non-browser clients (like the AI automation service, or a future mobile app).

**Trade-off worth knowing:** stateless tokens can't be "revoked" instantly the way a
session can (deleting a session row instantly logs someone out; a JWT stays valid
until it expires). Our `/api/auth/logout` endpoint is honest about this in a code
comment — it's a client-side action (throw away the token), not a server-side one.
A production system would add a token blocklist if instant revocation mattered.

## 2. Why does every route call a service function instead of writing the logic inline?

Look at any route file (e.g. `app/weeks/routes.py`) — it does three things: parse/validate
input via a schema, call one service function, return JSON. All the actual decisions
(does this week already exist? does the winner belong to this week?) live in
`app/services/week_service.py`. This is the "thin controller, fat service" pattern
from Phase 1's notes, now actually implemented. The payoff: when the AI automation
system needs to create a contestant in Phase 6, it hits the same
`POST /api/contestants` endpoint a human admin would use — same validation, same
business rules, zero duplicated logic.

## 3. Why do services raise exceptions instead of returning `None`/error codes?

`NotFoundError`, `ConflictError`, and the base `AppError` (in `app/utils/errors.py`)
get caught by a single app-wide error handler and turned into consistent JSON error
responses. This means individual routes never need `if not week: return 404` — they
just call the service, and if something's wrong, an exception bubbles up automatically
into the right HTTP status. One place decides what an error response looks like,
instead of every route reinventing it slightly differently.

## 4. Why validate the same rule (1-10 score) in three places?

The Marshmallow schema validates it (400 with a clear message), the database has a
`CHECK` constraint (guaranteed even if something bypasses the API), and the score
service also checks the contestant matches the episode. This isn't accidental
duplication — each layer catches a different *kind* of mistake:
- Schema: bad input from a client (human typo, buggy frontend, malformed AI output).
- Service: a business rule that spans multiple tables (contestant must belong to the
  episode being scored) — something a single-field schema check can't know.
- Database: the last line of defense, in case anything above is bypassed entirely.

## 5. Why write tests that hit the real HTTP endpoints instead of just testing service functions directly?

The tests in `tests/test_crud_chain.py` go through `client.post("/api/weeks", json=...)`
rather than calling `week_service.create_week()` directly. This exercises the entire
path — JSON parsing, schema validation, the service logic, and the JSON response
shape — which is exactly what a real client (the React frontend or the automation
service) will actually do. A bug in how a route calls a service, or in how a response
gets serialized, would be invisible to a test that only calls the service function.

## 6. Why does the score_distribution bug matter, and what does it teach?

Worth mentioning in a meeting as a concrete example of testing paying off: the
statistics service originally built `score_distribution` with integer keys
(`{1: 0, 2: 0, ...}`). That's valid Python, but JSON object keys are *always* strings
— so after `jsonify()`, the frontend would have received `{"1": 0, "2": 0, ...}`.
A test asserting on the actual HTTP response (not just the raw Python function) caught
this immediately. This is the concrete case for testing through the real API, not just
unit functions in isolation — the bug would otherwise have shown up as "why is my
chart empty" during frontend work in Phase 4.

## 7. Why separate Update schemas (e.g. `WeekUpdateSchema`) from Create schemas?

Create schemas mark fields `required=True` where a full record needs them. PUT
requests only send the fields being changed, so a separate schema makes every field
optional but still validated *if present* (`partial=True` on `.load()` reinforces
this). This avoids a common bug where a partial update accidentally wipes out fields
the client didn't intend to touch, and prevents fields that shouldn't be editable
(like reassigning `season_id` on a week) from silently becoming editable through PUT.

## 8. Likely meeting questions & short answers

- **"How does auth actually protect a route?"** → `@jwt_required()` decorator; verified
  by a test that a protected POST returns 401 with no token.
- **"What happens if two different validation layers disagree?"** → They don't get the
  chance to — schema runs first and rejects bad shape/range before the service (and
  therefore the DB) ever sees it. Each layer is a stricter filter than the one before.
- **"How do you know the CRUD endpoints actually work end-to-end, not just in theory?"**
  → 16 passing tests exercise the full entity chain (season → week → contestant →
  episode → dish → score) through real HTTP requests, including negative tests
  that confirm bad data gets rejected with the right status code.
- **"Is the automation API real yet?"** → The routes exist and return proper JSON,
  but the actual AI pipeline behind them is Phase 6 — right now they're honest
  placeholders (501/idle), matching the blueprint's phased approach, not fake
  success responses.
