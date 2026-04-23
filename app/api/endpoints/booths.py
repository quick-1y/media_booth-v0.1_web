from urllib.parse import unquote
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from app.schemas.config import AppConfig, ParserTestRequest
from app.schemas.booth import BoothCreate
from app.services.deps import (
    get_booths_service,
    get_settings_service,
    get_parking_service,
    get_media_service,
)

router = APIRouter()


# ─── Booth CRUD ───────────────────────────────────────────────────────────────

@router.get("")
async def list_booths() -> dict:
    return {"booths": await get_booths_service().list_booths()}


@router.post("")
async def create_booth(payload: BoothCreate) -> dict:
    booth = await get_booths_service().create_booth(payload.name)
    return {"booth": booth}


@router.delete("/{booth_id}")
async def delete_booth(booth_id: int) -> dict:
    try:
        await get_booths_service().delete_booth(booth_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"message": "Стенд удалён"}


# ─── Settings ─────────────────────────────────────────────────────────────────

@router.get("/{booth_id}/settings")
async def get_settings(booth_id: int) -> dict:
    try:
        service = get_settings_service()
        config = await service.get(booth_id)
        meta = await service.metadata(booth_id)
        return {"config": config.model_dump(mode="python"), "metadata": meta}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/{booth_id}/settings")
async def update_settings(booth_id: int, payload: AppConfig) -> dict:
    try:
        service = get_settings_service()
        config = await service.save(booth_id, payload)
        meta = await service.metadata(booth_id)
        return {
            "config": config.model_dump(mode="python"),
            "metadata": meta,
            "message": "Настройки сохранены",
        }
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


# ─── Parking ──────────────────────────────────────────────────────────────────

@router.get("/{booth_id}/parking/status")
async def parking_status(booth_id: int) -> dict:
    try:
        return await get_parking_service().fetch_status(booth_id, force=False)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{booth_id}/parking/test")
async def parking_test(booth_id: int, payload: ParserTestRequest) -> dict:
    if not payload.server.strip():
        raise HTTPException(status_code=400, detail="Адрес сервера не указан")
    try:
        return await get_parking_service().test_parser(
            payload.server.strip(), payload.path.strip(), payload.token.strip()
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"{type(exc).__name__}: {exc}") from exc


# ─── Media ────────────────────────────────────────────────────────────────────

@router.get("/{booth_id}/media/items")
async def media_items(booth_id: int) -> dict:
    return {"items": get_media_service().list_items(booth_id)}


@router.post("/{booth_id}/media/upload")
async def media_upload(booth_id: int, file: UploadFile = File(...)) -> dict:
    service = get_media_service()
    try:
        data = await file.read()
        service.save_file(booth_id, file.filename or "", data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"message": "Файл загружен", "name": file.filename}


@router.delete("/{booth_id}/media/file/{relative_path:path}")
async def media_delete(booth_id: int, relative_path: str) -> dict:
    service = get_media_service()
    try:
        service.delete_file(booth_id, unquote(relative_path))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"message": "Файл удалён"}


@router.get("/{booth_id}/media/file/{relative_path:path}")
async def media_file(booth_id: int, relative_path: str) -> FileResponse:
    try:
        path = get_media_service().get_file_path(booth_id, unquote(relative_path))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="Файл не найден")
    return FileResponse(path)
