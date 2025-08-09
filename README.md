# GPT-5 Math Solver API

Prototype FastAPI application with Google login, JWT auth, calculation history, WebSocket streaming, MongoDB (Beanie) and Redis cache.

## Running

```
uvicorn app.main:app --reload
```

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
