from dotenv import load_dotenv

# Same reasoning as seed.py: python-dotenv's automatic .env loading only
# happens via the `flask` CLI command. This file is run directly (python3
# wsgi.py, or gunicorn wsgi:app in production) — neither goes through the
# flask CLI, so without this explicit call, DATABASE_URL/JWT_SECRET_KEY from
# .env would be silently ignored and the app would fall back to config.py's
# hardcoded Postgres default, which is exactly the bug that caused this file
# to fail with "No module named 'psycopg2'" on a clean install.
load_dotenv()

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
