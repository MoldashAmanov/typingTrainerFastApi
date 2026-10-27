from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.database import create_db_and_tables
from app.routers import sessions, texts


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="Typing Trainer",
    description="Тренажер слепого ввода",
    version="1.0.0",
    lifespan=lifespan,
    )


app.include_router(texts.router)
app.include_router(sessions.router)

BASE_DIR = Path(__file__).resolve().parent.parent
app.mount('/static', StaticFiles(directory=BASE_DIR / 'static'), name='static')


@app.get('/', include_in_schema=False)
def index():
    return FileResponse(BASE_DIR / 'static' / 'index.html')


@app.get('/health', tags=['System'])
async def health_check():
    return {'status': 'ok'}