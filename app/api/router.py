from fastapi import APIRouter
from app.api.endpoints.health import router as health_router
from app.api.endpoints.settings import router as settings_router
from app.api.endpoints.parking import router as parking_router
from app.api.endpoints.media import router as media_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(settings_router, prefix="/settings", tags=["settings"])
api_router.include_router(parking_router, prefix="/parking", tags=["parking"])
api_router.include_router(media_router, prefix="/media", tags=["media"])
