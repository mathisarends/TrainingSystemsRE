# TrainingSystems

A personal periodized-training backend: Google/password sign-in, exercise catalogs, training
plans (weeks/days/entries) with RPE progression and deload, automatic
training-session detection, body weight tracking, personal records, and web push
notifications.

Built with FastAPI, SQLModel/Postgres, Dishka (DI), APScheduler, and pywebpush,
following the [fastapi-canon](https://github.com/mathisarends/fastapi-canon)
feature-slice architecture (`domain/application/infrastructure/presentation` per
feature). See `SPEC.md` for the full API specification.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Docker (for Postgres, or run your own)

## Setup

```bash
cp .env.example .env
# fill in AUTHENTICATION_JWT_SECRET, GOOGLE_CLIENT_ID/CLIENT_SECRET/REDIRECT_URI,
# and PUSH_VAPID_* (see below)

uv sync
docker compose up -d db
uv run alembic upgrade head
uv run uvicorn training_system.main:app --reload
```

The API is served under `/api/v1`; interactive docs at `/docs`.

Generate a VAPID key pair for web push with:

```bash
uv run python -c "from py_vapid import Vapid; v = Vapid(); v.generate_keys(); print(v.public_key, v.private_key)"
```

## Running everything in Docker

```bash
docker compose up --build
```

This starts Postgres and the API together; run migrations against the compose
network with `DATABASE_URL=postgresql+asyncpg://training:training@localhost:5432/training_system uv run alembic upgrade head`.

## Development

```bash
uv run pytest       # httpx ASGITransport tests, in-memory SQLite, fake Google OAuth provider
uv run ruff check .
uv run mypy --strict training_system
```

## Database migrations

Schema changes go through Alembic (`migrations/`), not `SQLModel.metadata.create_all`:

```bash
uv run alembic revision --autogenerate -m "describe the change"
uv run alembic upgrade head
```

## Project layout

```
training_system/
├── main.py                 # assembles all features into one FastAPI app via Dishka
├── settings.py              # AppSettings, DatabaseSettings
├── domain/                  # shared Entity/Aggregate base
├── infrastructure/          # database (SqlRepository, orm.py) + scheduler providers
├── presentation/            # Feature composition dataclass, base Schema, /health
└── features/
    ├── authentication/       # Google OAuth redirect flow + password auth, JWT access/refresh cookies
    ├── users/                # GET/PATCH/DELETE /me
    ├── exercises/            # exercise catalog
    ├── plans/                # training plans, RPE progression, session tracking
    ├── records/              # personal records
    ├── push/                 # web push subscriptions + sender
    ├── notifications/        # unseen training-session completions
    └── timer/                # rest-timer keep-alive
```

Each feature follows `domain → application → infrastructure → presentation`, with
dependencies pointing inward only.
