from functools import lru_cache
from app.services.booth_service import BoothService
from app.services.settings_service import BoothSettingsService
from app.services.parking_service import ParkingService
from app.services.media_service import MediaService


@lru_cache(maxsize=1)
def get_booth_service() -> BoothService:
    return BoothService()


@lru_cache(maxsize=1)
def get_settings_service() -> BoothSettingsService:
    return BoothSettingsService()


@lru_cache(maxsize=1)
def get_parking_service() -> ParkingService:
    return ParkingService(get_settings_service)


@lru_cache(maxsize=1)
def get_media_service() -> MediaService:
    return MediaService()
