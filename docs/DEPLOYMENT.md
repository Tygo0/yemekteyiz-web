# Deploying with Docker Compose

This is the third way to run Yemekteyiz, alongside `docs/RUNNING_LOCALLY.md`
(source checkout, for developing) and `docs/BUILDING_RELEASE_EXECUTABLE.md`
(single-file binary, for a zero-install local run). Docker Compose is for
running it as a real service — with Postgres instead of SQLite, and the
frontend/backend as independently restartable containers.

Verified end-to-end on real Docker (Docker Desktop + WSL2 on Windows): build,
migrations against real Postgres, admin seeding, login, full CRUD round-trip
through the frontend's nginx proxy, and data surviving a container restart.

## What's in the stack

```
docker-compose.yml
├── postgres   postgres:16-alpine, internal-only (no published port)
├── backend    Flask API (gunicorn), published on :5000
└── frontend   React SPA built + served by nginx, published on :8080
```

The `automation/` AI pipeline is **not** part of this stack — it needs a real
`GEMINI_API_KEY` and downloads large OCR/speech models, neither of which fit
a generic `docker compose up`. It keeps running as a separate process (see
the main `README.md`) and talks to the backend over the same `:5000` port
this stack publishes.

## How the pieces connect

- **frontend → backend**: the frontend's nginx config (`frontend/nginx.conf`)
  reverse-proxies `/api/*` to `http://backend:5000/api/*` using Docker
  Compose's internal service DNS. The React app is built with
  `VITE_API_BASE_URL=/api` (a relative path — see `frontend/Dockerfile`), so
  the browser only ever talks to the frontend's own origin. No CORS
  configuration needed, no hardcoded backend hostname baked into the bundle.
- **backend → postgres**: `DATABASE_URL` is assembled by docker-compose from
  the `POSTGRES_*` variables in `.env`, pointed at the `postgres` service
  name. `backend/config.py` reads it the same way it does in every other
  run mode.
- **backend startup** (`backend/docker-entrypoint.sh`): runs `flask db
  upgrade`, then `python3 seed.py` if `ADMIN_USERNAME`/`ADMIN_PASSWORD` are
  set (skips if that admin already exists — safe to restart), then starts
  gunicorn. All three steps are idempotent, confirmed by restarting the
  backend container against an already-migrated, already-seeded database.

## Running it

```bash
cp .env.example .env
# edit .env — at minimum change JWT_SECRET_KEY and POSTGRES_PASSWORD away
# from the placeholder values before running this anywhere but your own
# machine

docker compose up --build -d
```

Then:
- Frontend: http://localhost:8080
- Backend API directly: http://localhost:5000/api/health

Log in with the `ADMIN_USERNAME`/`ADMIN_PASSWORD` you set in `.env` (only
created on first startup — change the password afterward via a real admin
management flow if you plan to keep this running long-term, since there
isn't a "change password" endpoint yet).

Check logs / tear down:
```bash
docker compose logs backend -f
docker compose down            # stop, keep the postgres-data volume
docker compose down -v         # stop AND delete all data — careful
```

## Production notes

- **Secrets**: `.env` is gitignored. Never commit a real `JWT_SECRET_KEY` or
  `POSTGRES_PASSWORD`. Generate a real secret key with:
  `python3 -c "import secrets; print(secrets.token_hex(32))"`
- **TLS**: this compose file serves plain HTTP on `:8080`/`:5000`. Put a
  reverse proxy (Caddy, Traefik, or nginx with certbot) in front for a real
  public deployment — that's outside this stack's scope.
- **Backups**: `postgres-data` is a named Docker volume. Back it up with
  `docker compose exec postgres pg_dump` on whatever schedule your data
  matters enough to protect.
- **Automation pipeline**: point `automation/.env`'s `AUTOMATION_BACKEND_URL`
  at wherever this stack's backend is reachable (`http://localhost:5000` for
  same-machine, or your public domain/IP otherwise).
