# python:3.11 (not 3.13+, which the rest of the repo targets for local dev) —
# psycopg2-binary reliably has prebuilt wheels for 3.11, avoiding exactly the
# "compile from source, needs libpq-dev" pitfall requirements-postgres.txt
# warns about on very new Python versions.
FROM python:3.11-slim

WORKDIR /app

# System deps for psycopg2-binary's build fallback + healthchecks elsewhere
# in the stack use curl, kept here so it's available if needed for debugging.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements-postgres.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-postgres.txt

COPY . .

RUN chmod +x docker-entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["./docker-entrypoint.sh"]
