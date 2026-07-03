# Phase 5 — Concepts & Reasoning (Meeting Prep Notes)

## 1. Why "clean-room" testing instead of just re-running commands in the same terminal?

Every terminal session in earlier phases accumulated hidden state — exported
environment variables, already-installed packages, a `dev.db` that already existed.
Re-testing in that same terminal would have passed even if the *documented* steps
were broken, because the terminal already had things a fresh clone wouldn't. Clean-room
testing means copying the repo to a brand new directory and following the README
*exactly as written*, with zero leftover context — which is exactly what someone
cloning the repo for the first time experiences. This caught two real bugs that all
our previous (non-clean-room) testing had missed.

## 2. Bug #1: the committed `.env.example` pointed at a hostname that doesn't exist yet

The root `.env.example`'s `DATABASE_URL` used `postgres` as the hostname — which only
resolves inside a Docker Compose network (where a container named `postgres` exists).
Anyone following the docs outside of Docker would hit
`could not translate host name "postgres"` on the very first command. The fix wasn't
to patch the instructions around the bug — it was to add a **backend-specific**
`.env.example` defaulting to SQLite (`sqlite:///dev.db`), which needs nothing else
running at all. The root `.env.example` still exists for when Docker Compose is built
later; it's just no longer the one a local-only setup copies.

## 3. Bug #2: `seed.py` silently ignored the `.env` file

This one's a genuinely useful Flask/Python fact: Flask's own CLI (`flask db upgrade`,
`flask run`) automatically loads a `.env` file via `python-dotenv` — but that
auto-loading is a feature of the `flask` command specifically, not of `python-dotenv`
itself. Running `python3 seed.py` directly does **not** get that auto-load, so
`seed.py` was silently falling back to `config.py`'s hardcoded Postgres default,
even with a perfectly correct `.env` sitting right next to it. The fix: add an
explicit `load_dotenv()` call at the top of `seed.py` itself, so it works correctly
regardless of *how* it's invoked. This is a good one to know cold: **"does this
script use the `flask` CLI, or plain `python3`?" determines whether `.env` gets read
automatically or needs an explicit load_dotenv() call.**

## 4. Why was Docker/Kubernetes explicitly descoped from this phase?

Not because they're bad ideas — Docker Compose is already in the original blueprint's
own architecture. The reason is more basic: this working environment has no Docker
daemon and no access to Docker Hub, so any Dockerfile or compose config written here
could not actually be *run and verified* the way every other piece of this project has
been. Shipping unverified infrastructure config in a release — right after the exact
kind of untested-assumption bug that clean-room testing just caught in the plain
Python setup — would be repeating the same mistake at a larger scale. Kubernetes
specifically was also rejected on pure scope grounds: it solves multi-machine
orchestration and auto-scaling, neither of which this project needs at four
containers on (eventually) one machine.

## 5. What's the actual difference between a git tag and a GitHub Release?

A **git tag** (`git tag v0.1.0`) is just a permanent name pointing at one specific
commit — lightweight, built into git itself, works with any git host or none at all.
A **GitHub Release** is GitHub's own feature built on top of a tag: it adds a title,
formatted release notes, and (optionally) attached files, and shows up in a dedicated
"Releases" section of the repo page that's easier for someone to discover than
scrolling through commits or tags. Practically: the tag is required, the Release is a
friendlier presentation layer GitHub adds on top of it.

## 6. Why version `v0.1.0` and not `v1.0.0`?

Semantic versioning convention: a `0.x.y` version signals "not yet a complete,
stable 1.0 product" — appropriate here since the AI automation half of the blueprint
(the actual differentiating feature) doesn't exist yet. `v1.0.0` should be reserved
for when the whole system described in the blueprint is actually built.

## 7. Likely meeting questions & short answers

- **"How do you know the setup instructions actually work?"** → Ran them in a
  genuinely fresh copy of the repo with no prior state, start to finish, and fixed
  two real bugs the process caught — not just re-read the docs and assumed they're
  correct.
- **"Why isn't there a docker-compose.yml yet?"** → It would have been unverified
  code in an environment with no way to actually run it — deliberately deferred
  rather than shipped untested.
- **"What's the difference between a tag and a release?"** → A tag names a commit;
  a Release is GitHub's presentation layer on top of a tag, with notes and a
  discoverable page.
