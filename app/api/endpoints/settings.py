from fastapi import APIRouter
from app.schemas.config import AppConfig
from app.services.deps import get_settings_service
router = APIRouter()

@router.get('')
async def get_settings() -> dict:
    service = get_settings_service()
    config = service.get()
    meta = service.metadata()
    return {"config": config.model_dump(mode="python"), "metadata": {"config_path": meta.config_path, "loaded_at": meta.loaded_at, "saved_at": meta.saved_at}}

@router.put('')
async def update_settings(payload: AppConfig) -> dict:
    service = get_settings_service()
    config = service.save(payload)
    meta = service.metadata()
    return {"config": config.model_dump(mode="python"), "metadata": {"config_path": meta.config_path, "loaded_at": meta.loaded_at, "saved_at": meta.saved_at}, "message": "Настройки сохранены"}

@router.post('/reload')
async def reload_settings() -> dict:
    service = get_settings_service()
    config = service.reload()
    meta = service.metadata()
    return {"config": config.model_dump(mode="python"), "metadata": {"config_path": meta.config_path, "loaded_at": meta.loaded_at, "saved_at": meta.saved_at}, "message": "Настройки перечитаны с диска"}

@router.get('/raw')
async def raw_settings() -> dict:
    service = get_settings_service()
    meta = service.metadata()
    return {"raw_yaml": service.raw_yaml(), "config_path": meta.config_path, "loaded_at": meta.loaded_at, "saved_at": meta.saved_at}
