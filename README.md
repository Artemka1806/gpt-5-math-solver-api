# GPT-5 Math Solver API

Prototype FastAPI application with Google login, JWT auth, calculation history, WebSocket streaming, MongoDB (Beanie) and Redis cache.

## Running

```
uvicorn app.main:app --reload
```

### Environment

Copy `.env.example` to `.env` and set secrets:

- `JWT_SECRET` — strong random value
- `MONGO_INITDB_ROOT_USERNAME`, `MONGO_INITDB_ROOT_PASSWORD` — Mongo root user (used by Docker)
- `REDIS_PASSWORD` — Redis password (used by Docker)

Notes:
- Local non-Docker dev can use `MONGODB_URL` and `REDIS_URL` defaults pointing to `localhost`.
- Docker Compose overrides `MONGODB_URL` and `REDIS_URL` for the API using the credentials above and service hosts `mongo`/`redis`.

### Docker

Build and run the API along with MongoDB and Redis using Docker Compose:

```
docker-compose up --build
```

The service will be available at [http://localhost:8000](http://localhost:8000).

## WebSocket test client

For a quick manual test of the streaming WebSocket endpoint open
`ws_client.html` in your browser, enter an access token, choose an image with a
math expression and click **Connect** then **Send**.
