from functools import lru_cache
from app.core.config import get_runtime_settings
from app.services.settings_service import SettingsService
from app.services.parking_service import ParkingService
from app.services.media_service import MediaService

@lru_cache(maxsize=1)
def get_settings_service() -> SettingsService:
    return SettingsService(get_runtime_settings().config_path)

@lru_cache(maxsize=1)
def get_parking_service() -> ParkingService:
    return ParkingService(get_settings_service)

@lru_cache(maxsize=1)
def get_media_service() -> MediaService:
    return MediaService(get_settings_service)
