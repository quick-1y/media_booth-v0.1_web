from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.router import api_router
from app.route.pages import router as pages_router

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "web" / "static"

app = FastAPI(title="Parking Media Wall", version="0.1.0")
app.include_router(api_router, prefix="/api")
app.include_router(pages_router)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
