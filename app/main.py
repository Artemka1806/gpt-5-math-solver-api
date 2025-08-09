import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from .db import init_db, close_db
from .core.security import verify_token
from .models.calculation import Calculation
from .routers import auth, user, calculations, admin
from .services.openai_solver import stream_solution

app = FastAPI(title="Math Solver API")
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(calculations.router)
app.include_router(admin.router)


@app.on_event("startup")
async def on_startup():
    await init_db()


@app.on_event("shutdown")
async def on_shutdown():
    await close_db()


@app.get("/health")
async def health():
    return {"status": "OK"}


@app.websocket("/ws/calculate")
async def ws_calculate(websocket: WebSocket):
    token = websocket.query_params.get("token")
    payload = verify_token(token) if token else None
    if not payload:
        await websocket.accept()
        await websocket.send_text("ERROR: Unauthorized (invalid or expired token)")
        await websocket.close()
        return
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("action") != "solve":
                await websocket.send_text("ERROR: Unknown action")
                continue
            image_b64 = data.get("image")
            if not image_b64:
                await websocket.send_text("ERROR: image required")
                continue

            try:
                result = await stream_solution(image_b64, websocket)
                await Calculation(
                    user_id=payload.get("sub"), expression="", result_text=result
                ).insert()
                await websocket.send_text("[DONE]")
            except Exception as exc:
                await websocket.send_text(f"ERROR: {exc}")
    except WebSocketDisconnect:
        pass
