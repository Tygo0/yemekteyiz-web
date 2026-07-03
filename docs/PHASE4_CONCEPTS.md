# Phase 4 — Concepts & Reasoning (Meeting Prep Notes)

## 1. Why one set of pages instead of separate "public site" and "admin panel"?

The backend's own permission model already draws the line: every `GET` endpoint is
public, every `POST`/`PUT`/`DELETE` requires a JWT. So instead of building two parallel
page trees (a public `WeeksPublic.jsx` and a separate `WeeksAdmin.jsx` that mostly
duplicate each other), each page just checks `isAuthenticated` and conditionally shows
the create/edit/delete controls. A visitor and a logged-in admin see the *same* Weeks
page — the admin just also sees a form at the bottom. This directly mirrors the
backend's actual security boundary instead of inventing a second one in the frontend
that could drift out of sync with it.

## 2. Why does the JWT live in `localStorage` instead of React state alone?

If the token only lived in a `useState`, refreshing the browser would lose it and
force a re-login every time — bad experience for an admin doing data entry across
many page loads. `localStorage` persists across refreshes and tabs. The trade-off
(worth knowing): anything in `localStorage` is readable by any JavaScript running on
the page, so it's vulnerable if the site ever has an XSS bug. That's an accepted
trade-off for an admin tool like this; a more security-sensitive app might use an
httpOnly cookie instead, which JavaScript can't read at all.

## 3. Why is there an axios *interceptor* instead of passing the token manually on each call?

Look at `services/api.js` — the interceptor reads the token from `localStorage` and
attaches `Authorization: Bearer <token>` to every outgoing request automatically.
Without it, every single service function (`weekService.create`, `scoreService.create`,
etc.) would need to remember to add that header itself — one missed spot and you get a
confusing 401 that's hard to trace. Centralizing it in one place means auth simply
can't be forgotten.

## 4. Why is there one `createResourceService()` factory instead of six separate service files?

Seasons, weeks, contestants, episodes, dishes, and scores all expose the exact same
four operations (`list`, `get`, `create`, `update`/`delete`) against the exact same
URL pattern. Writing that out six times would mean six places to fix if, say, error
handling needed to change. The factory in `services/resources.js` generates all six
clients from one function — this is the frontend mirror of the backend's "services"
pattern from Phase 3: write the repeated logic once, reuse it everywhere.

## 5. Why does the ScorePaddle component exist, and why does its color change?

This is the one deliberate design risk in the app (see `docs/frontend-design` notes):
the show's actual visual gimmick is judges holding up numbered paddles to score
contestants. Rendering scores as literal paddle-shaped cards — gold for 8-10, brick-red
for 1-3 — ties the UI directly to real content from the show instead of using a generic
number badge. It's reused in the Dashboard, Statistics, and Scores pages so a score
always *looks* the same everywhere, which is what makes it feel like a real design
decision instead of a one-off flourish.

## 6. Why does creating a Score auto-derive `contestant_id` from the selected Episode instead of asking for both?

Phase 3's backend explicitly rejects a score where `contestant_id` doesn't match
`episode.contestant_id` (see `score_service.py`). If the form asked an admin to pick
both an episode *and* a contestant separately, it would be trivially easy to
accidentally pick a mismatched pair and get a confusing 400 error. Instead, the Scores
page form only asks for the episode; the contestant is looked up automatically from
that episode, so a mismatch is structurally impossible from the UI side — the frontend
protects the same invariant the backend already enforces, rather than fighting it.

## 7. Why verify the frontend against curl calls to the real backend instead of just trusting it "should work"?

Before considering this phase done, I ran the exact sequence the UI performs — login,
create a season, create a week, fetch statistics — directly against the running Flask
server, and separately confirmed the CORS preflight headers are present (the frontend
runs on `localhost:5173`, the backend on `:5000` — different origins, so without CORS
configured correctly, every request would be silently blocked by the browser). This
caught real integration risk (CORS, response shapes matching what the pages expect)
that a component-level check alone wouldn't have caught.

## 8. Likely meeting questions & short answers

- **"Why not use Material UI like the blueprint suggested?"** → Tailwind was chosen so
  the design could be a deliberate, specific visual identity (the çini-tile palette,
  the paddle motif) rather than a generic component-library look — worth being able to
  justify since the blueprint listed both as options.
- **"How does the app know if I'm logged in after a refresh?"** → `AuthContext` checks
  `localStorage` for a token on load and calls `/api/auth/me` to verify it's still
  valid before trusting it.
- **"What stops someone from submitting a score for the wrong contestant?"** → The
  Scores form only exposes an episode picker; the contestant is derived automatically,
  so the UI can't produce the mismatched pair the backend would reject anyway.
- **"Is this connected to a real backend or mocked?"** → Real — verified by running
  actual login/create/statistics calls against the Flask server started fresh, not
  assumed from reading the code.
