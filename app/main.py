from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from jose import JWTError
from sqlmodel import Session
from app.database import engine
from app.models import User
from app.security import decode_access_token
from app.routers import sessions, texts, auth, users, pages



app = FastAPI(
    title="Typing Trainer",
    description="Тренажер слепого ввода",
    version="1.0.0",
    )

@app.middleware("http")
async def load_current_user(request: Request, call_next):
    request.state.current_user = None
    request.state.messages = []

    token = request.cookies.get("access_token")
    if token:
        payload = decode_access_token(token)     # dict | None
        if payload is not None:                  # ← ПРОВЕРКА
            try:
                user_id = int(payload.get("sub", ""))
                with Session(engine) as session:
                    user = session.get(User, user_id)
                    if user is not None and user.is_active:
                        request.state.current_user = user
            except (ValueError, TypeError):
                pass

    return await call_next(request)


app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(texts.router)
app.include_router(sessions.router)
app.include_router(users.router)

BASE_DIR = Path(__file__).resolve().parent.parent
app.mount('/static', StaticFiles(directory=BASE_DIR / 'static'), name='static')


@app.get('/health', tags=['System'])
async def health_check():
    return {'status': 'ok'}