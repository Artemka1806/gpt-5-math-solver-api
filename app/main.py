import asyncio
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .db import init_db, close_db
from .core.security import verify_token
from .models.calculation import Calculation
from .models.user import User
from .routers import auth, user, calculations, admin, billing
from .services.openai_solver import stream_solution

app = FastAPI(title="Math Solver API")
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(calculations.router)
app.include_router(admin.router)
app.include_router(billing.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    user = await User.get(payload.get("sub"))
    if not user:
        await websocket.accept()
        await websocket.send_text("ERROR: User not found")
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
                if user.subscription_expires and user.subscription_expires > datetime.utcnow():
                    pass
                elif user.credits > 0:
                    user.credits -= 1
                    await user.save()
                else:
                    await websocket.send_text("ERROR: No credits available")
                    continue
                result = await stream_solution(image_b64, websocket)
                await Calculation(
                    user_id=payload.get("sub"), expression="", result_text=result
                ).insert()
                await websocket.send_text("\n[DONE]\n")
            except Exception as exc:
                await websocket.send_text(f"\n[ERROR]: {exc}")
    except WebSocketDisconnect:
        pass
