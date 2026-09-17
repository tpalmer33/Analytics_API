# Build an Analytics API using FastAPI + Time-series Postgres

Start by building an Analytics API service with Python, FastAPI, and Time-series Postgres with TimescaleDB

## Docker

- `docker build -t analytics-api -f Dockerfile .`
- `docker run analytics-api`

becomes

- `docker compose up --watch`
- `docker compose down` or `docker compose down -v` (to remove volumes)
- `docker compose run app /bin/bash`(invalid in git bash) or `docker compose run app python` (to enter cl in container)