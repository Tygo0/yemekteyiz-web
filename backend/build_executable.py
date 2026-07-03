"""
Builds the single-file standalone executable (no Python/Node install required
to run it) for whatever platform you run this script ON. PyInstaller builds
are platform-specific — running this on Windows produces a .exe that only
runs on Windows; running it on Linux produces a binary that only runs on
Linux, and so on. There is no cross-compiling: to produce a Windows .exe, run
this script on an actual Windows machine.

Usage:
    python3 build_executable.py

Run this from the backend/ directory. Requires:
    pip install -r requirements.txt --break-system-packages
    pip install pyinstaller --break-system-packages
    Node.js/npm installed (used to build the frontend)
"""
import os
import platform
import shutil
import subprocess
import sys

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BACKEND_DIR, "..", "frontend")
FRONTEND_DIST = os.path.join(FRONTEND_DIR, "dist")
BUNDLED_FRONTEND = os.path.join(BACKEND_DIR, "frontend_dist")


def run(cmd, cwd=None):
    print(f"$ {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, check=True)


def build_frontend():
    print("\n=== 1. Building frontend (relative /api base URL for same-origin serving) ===")
    env_production = os.path.join(FRONTEND_DIR, ".env.production")
    with open(env_production, "w") as f:
        f.write("VITE_API_BASE_URL=/api\n")

    npm = "npm.cmd" if platform.system() == "Windows" else "npm"
    run([npm, "install", "--legacy-peer-deps"], cwd=FRONTEND_DIR)
    run([npm, "run", "build"], cwd=FRONTEND_DIR)

    os.remove(env_production)  # don't leave this affecting normal `npm run dev`

    if os.path.isdir(BUNDLED_FRONTEND):
        shutil.rmtree(BUNDLED_FRONTEND)
    shutil.copytree(FRONTEND_DIST, BUNDLED_FRONTEND)
    print(f"Copied {FRONTEND_DIST} -> {BUNDLED_FRONTEND}")


def build_executable():
    print("\n=== 2. Building standalone executable with PyInstaller ===")
    # PyInstaller's --add-data separator differs by OS: "src:dest" on
    # Linux/macOS, "src;dest" on Windows.
    sep = ";" if platform.system() == "Windows" else ":"

    for build_dir in ("build", "dist"):
        path = os.path.join(BACKEND_DIR, build_dir)
        if os.path.isdir(path):
            shutil.rmtree(path)

    run([
        sys.executable, "-m", "PyInstaller", "--onefile",
        "--name", "yemekteyiz-server",
        "--add-data", f"migrations{sep}migrations",
        "--add-data", f"frontend_dist{sep}frontend_dist",
        "--hidden-import", "logging.config",
        "launcher.py",
    ], cwd=BACKEND_DIR)

    exe_name = "yemekteyiz-server.exe" if platform.system() == "Windows" else "yemekteyiz-server"
    exe_path = os.path.join(BACKEND_DIR, "dist", exe_name)
    print(f"\nBuilt: {exe_path}")
    print("This file only runs on this same OS/architecture "
          f"({platform.system()} {platform.machine()}).")


if __name__ == "__main__":
    build_frontend()
    build_executable()
