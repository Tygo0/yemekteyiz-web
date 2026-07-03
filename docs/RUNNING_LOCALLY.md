# Running Yemekteyiz Locally

This guide gets the site running on your own machine: a Flask API and a React
frontend, running as two separate local processes. Every command below has been
run end-to-end against a fresh checkout of this repo — if something doesn't work
exactly as described, that's a real bug, not a missing step on your end.

## Prerequisites

- **Python 3.10+** — check with `python3 --version`
- **Node.js 18+** — check with `node --version`

No database software to install: the default local setup uses SQLite, which
needs nothing running in the background — the whole database is just one file.

## 1. Clone the repo

```bash
git clone <your-repo-url>
cd yemekteyiz
```

## 2. Backend setup

```bash
cd backend
pip install -r requirements.txt --break-system-packages   # or use a venv, see note below

cp .env.example .env
export FLASK_APP=wsgi.py

flask db upgrade
ADMIN_USERNAME=admin ADMIN_PASSWORD=changeme123 python3 seed.py

python3 wsgi.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
```

Leave this terminal running. Your admin login is `admin` / `changeme123` (or
whatever you set `ADMIN_USERNAME`/`ADMIN_PASSWORD` to).

**Using a virtual environment instead of `--break-system-packages`:**
```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Frontend setup (new terminal)

```bash
cd frontend
npm install
cp .env.example .env

npm run dev
```

You should see:
```
Local:   http://localhost:5173/
```

## 4. Open it

Go to **http://localhost:5173** in your browser.

- You'll land on the Weeks page as a visitor.
- Click **Admin login** (top right), sign in with the credentials from step 2.
- Once logged in, every page shows "Add a..." forms and Edit/Delete buttons.

A sensible order to add test data:
1. **Weeks page** → add a season, then a week
2. **Contestants page** → add a contestant to that week
3. **Episodes page** → add an episode for that contestant
4. **Dishes** / **Scores pages** → add a dish and a score for that episode
5. **Statistics page** → see it all aggregated
6. Back on **Weeks**, click Edit → now that a contestant exists, set them as winner

To confirm visitor vs. admin views are actually different, open a second
**private/incognito** browser window to the same `localhost:5173` — you won't be
logged in there, so you'll see the read-only view.

## Running the test suite

```bash
cd backend
python3 -m pytest tests/ -v
```
This uses an in-memory database — it doesn't touch your `dev.db`.

## Resetting your local data

Your local database is a single file: `backend/dev.db`. Delete it and re-run
`flask db upgrade` (+ the seed command) to start fresh:
```bash
cd backend
rm dev.db
flask db upgrade
ADMIN_USERNAME=admin ADMIN_PASSWORD=changeme123 python3 seed.py
```

## Using Postgres instead of SQLite

SQLite is the default because it needs no separate install — the core
`requirements.txt` deliberately doesn't include a Postgres driver, so a plain
SQLite setup never needs to compile anything. If you'd rather run against a real
Postgres instance you already have installed and running:

1. Install the Postgres driver (not included by default):
   ```bash
   pip install -r requirements-postgres.txt --break-system-packages
   ```
2. Create a database and user matching what you want to use.
3. In `backend/.env`, comment out the SQLite `DATABASE_URL` line and uncomment
   the Postgres line, editing it to match your actual username/password/database.
4. Run `flask db upgrade` again — Alembic will create the schema in Postgres instead.

## Troubleshooting

**"Address already in use" on port 5000 or 5173** — something else is already
running on that port. Stop it, or for the backend, run
`flask run --port 5001` (and update `VITE_API_BASE_URL` in `frontend/.env` to match).

**`ModuleNotFoundError` when running `python3 seed.py` or `flask db upgrade`** —
you're likely not in the `backend/` directory, or dependencies didn't install.
Re-run `pip install -r requirements.txt --break-system-packages` from `backend/`.

**Login fails with "Invalid username or password"** — the admin was created with
different credentials than you're typing, or `seed.py` was run before the
migrations (`flask db upgrade` must run first). Re-run both in that order.

**Frontend loads but every page shows a network error** — the backend isn't
running, or `frontend/.env`'s `VITE_API_BASE_URL` doesn't match where the backend
is actually listening. Confirm `http://localhost:5000/api/health` returns
`{"status": "ok"}` in your browser first.

**`pip install` fails trying to build `psycopg2-binary`** (compiler errors,
`libpq-fe.h: No such file or directory`) — this shouldn't happen anymore:
`requirements.txt` no longer includes a Postgres driver at all, since the default
setup uses SQLite and doesn't need one. If you still see this, you're likely
using an older copy of `requirements.txt` — pull the latest, or manually remove
any `psycopg2-binary` line from it. Only install
`requirements-postgres.txt` if you're deliberately switching to Postgres (see
above), and even then, install PostgreSQL's dev headers first if it still fails
to build (`sudo apt install libpq-dev python3-dev` on Debian/Ubuntu).
