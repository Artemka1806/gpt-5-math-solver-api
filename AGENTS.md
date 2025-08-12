# Repository Guidelines

## Project Structure & Module Organization
- `app/`: FastAPI application code.
  - `app/main.py`: App entrypoint and router wiring.
  - `app/routers/`: API route modules (auth, user, calculations, admin, billing).
  - `app/services/`: External integrations (e.g., `openai_solver.py`, `google_pay.py`).
  - `app/models/`: Beanie document models (`User`, `Calculation`).
  - `app/core/`: Configuration and security (`config.py`, `security.py`).
  - `app/db.py`: MongoDB/Redis init and teardown.
- Root: `requirements.txt`, `Dockerfile`, `docker-compose.yml`, `.env.example`, `ws_client.html`.

## Build, Test, and Development Commands
- Run locally (autoreload): `uvicorn app.main:app --reload`
- Docker (API + MongoDB + Redis): `docker-compose up --build`
- Health check: `GET /health`

Service runs at `http://localhost:8000`. WebSocket: `ws://localhost:8000/ws/calculate?token=...`.

## Coding Style & Naming Conventions
- Python, PEP 8, 4-space indentation.
- Use type hints for public functions and models.
- Filenames/modules: `snake_case.py`; classes: `PascalCase`; functions/vars: `snake_case`.
- Group endpoints by domain under `app/routers/` and use clear path prefixes.
- No repo-enforced formatter; keep diffs small and focused.

## Commit & Pull Request Guidelines
- Commits: imperative mood and scoped (e.g., “Add CORS middleware”, “Fix Google login status code”).
- Reference issues with `#id` when applicable.
- PRs should include: purpose summary, affected endpoints/modules, testing notes (commands or `ws_client.html` screenshots), and any config changes.
- Keep PRs small; separate refactors from feature work.

## Security & Configuration Tips
- Copy `.env.example` to `.env` and set: JWT secret, Mongo/Redis URLs, `GOOGLE_CLIENT_ID`, and `redirect_url`.
- Never commit secrets; prefer env vars in production.
- Use `wss://` behind TLS in production; set strong JWT secrets.
- Review `app/core/config.py` defaults; don’t rely on them in prod.

## Architecture Overview
- FastAPI app with routers, Beanie (MongoDB) persistence, Redis cache, and a WebSocket streaming solver.
- Startup/shutdown lifecycle manages DB and Redis (`app/db.py`).
