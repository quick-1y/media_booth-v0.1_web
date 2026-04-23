from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.db import init_pool, close_pool
from app.api.router import api_router
from app.route.pages import router as pages_router

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "web" / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_pool()
    yield
    await close_pool()


app = FastAPI(title="Media Booth Manager", version="0.2.0", lifespan=lifespan)
app.include_router(api_router, prefix="/api")
app.include_router(pages_router)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
