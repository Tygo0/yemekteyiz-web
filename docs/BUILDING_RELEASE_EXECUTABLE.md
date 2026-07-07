# Building the Standalone Executable Release

This produces a single file someone can download from GitHub Releases and run
directly — no Python, no Node.js, no `pip install`/`npm install`. Double-click
it (or run it from a terminal), and it opens your browser to a fully working
site with an auto-created local database.

This is a **different distribution method** than `docs/RUNNING_LOCALLY.md`,
which is for people who want to read/edit the source code. This one is for
someone who just wants to *run* the finished app.

## How it works

- Flask serves both the API (`/api/...`) and the pre-built React app (every
  other route) from a single process — see `serve_react_app()` in
  `backend/app/__init__.py`.
- `backend/launcher.py` (not `wsgi.py`) is the actual entry point: on startup
  it auto-runs database migrations, creates a default admin account if one
  doesn't exist yet, and starts a production-capable server
  ([waitress](https://github.com/Pylons/waitress) — pure Python, works on
  Windows unlike gunicorn).
- [PyInstaller](https://pyinstaller.org/) bundles the Python interpreter, every
  dependency, the database migrations, and the built frontend into one file.

## Building it yourself

**Important: PyInstaller does not cross-compile.** A binary built on Linux only
runs on Linux; built on Windows, only runs on Windows. To produce a Windows
`.exe`, you must run the build **on an actual Windows machine** (or a Windows
VM) — not from Linux/WSL/Kali.

### Prerequisites (on whichever machine you're building on)
- Python 3.10+ and Node.js 18+ (same as `docs/RUNNING_LOCALLY.md`)
- `pip install -r requirements.txt --break-system-packages`
- `pip install pyinstaller --break-system-packages`

### Build
```bash
cd backend
python3 build_executable.py
```

This builds the frontend, copies it into the backend, and runs PyInstaller.
Output:
- Linux: `backend/dist/yemekteyiz-server`
- Windows: `backend\dist\yemekteyiz-server.exe`
- macOS: `backend/dist/yemekteyiz-server`

The build takes a minute or two and produces a ~50MB single file — that's
normal; it's carrying its own Python interpreter and every dependency.

## Testing it before publishing

Copy **only the executable** (not the source code) to an empty folder and run
it from there, to make sure it's really self-contained:

```bash
mkdir /tmp/release_test && cp backend/dist/yemekteyiz-server /tmp/release_test/
cd /tmp/release_test
./yemekteyiz-server
```
It should print an admin username/password, then open your browser to
`http://localhost:5000` with a fully working site. A `yemekteyiz.db` and
`.secret_key` file will appear next to the executable — that's expected,
that's its database.

## Publishing to GitHub Releases

The executable itself should **not** be committed to git (it's ~50MB and
regeneratable — `build/`, `dist/`, and `frontend_dist/` are gitignored).

**Automated (the normal path):** `.github/workflows/release.yml` builds both
the Linux and Windows executables on real `ubuntu-latest`/`windows-latest`
GitHub Actions runners (solving the no-cross-compiling problem above without
needing two physical machines) and attaches them to a GitHub Release
automatically. It runs in two ways:

- **On tag push** — `git tag vX.Y.Z && git push origin vX.Y.Z` builds and
  publishes a release for that tag automatically.
- **On demand** — from the repo's **Actions** tab → **Release executables** →
  **Run workflow**, entering an existing tag name, for building assets for a
  tag that predates the workflow, or re-running a failed build.

The `release` job (`softprops/action-gh-release@v2`) creates the GitHub
Release if it doesn't exist yet and attaches `yemekteyiz-server-linux` and
`yemekteyiz-server-windows.exe`.

**Manual fallback**, if you ever need to attach a binary without going
through CI (e.g. testing an unpushed local build): On GitHub, your repo →
**Releases** → **Draft a new release** (or edit an existing one) → drag the
file under "Attach binaries," or use `gh release upload <tag> <path-to-binary>`.

Anyone visiting your repo can then go to **Releases**, download the file for
their OS, and run it — no cloning, no installing dependencies.

## What to tell people in the release notes

Something like:

> **Windows/Linux/macOS:** Download `yemekteyiz-server` (or `.exe` for
> Windows) below, run it, and your browser will open automatically to a fully
> working site. First run creates a local database and an admin account —
> check the terminal window for the login credentials it prints.
