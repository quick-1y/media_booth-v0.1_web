from urllib.parse import unquote
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from app.schemas.config import AppConfig, ParserTestRequest
from app.schemas.booth import BoothCreate, BoothRename
from app.services.deps import (
    get_booth_service,
    get_settings_service,
    get_parking_service,
    get_media_service,
)

router = APIRouter()


# ── Booth CRUD ────────────────────────────────────────────────────────────────

@router.get("")
async def list_booths() -> dict:
    return {"booths": await get_booth_service().list()}


@router.post("")
async def create_booth(payload: BoothCreate) -> dict:
    return {"booth": await get_booth_service().create(payload.name)}


@router.patch("/{booth_id}")
async def rename_booth(booth_id: int, payload: BoothRename) -> dict:
    try:
        await get_booth_service().rename(booth_id, payload.name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"message": "Название обновлено", "name": payload.name}


@router.delete("/{booth_id}")
async def delete_booth(booth_id: int) -> dict:
    try:
        await get_booth_service().delete(booth_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"message": "Стенд удалён"}


# ── Settings ──────────────────────────────────────────────────────────────────

@router.get("/{booth_id}/settings")
async def get_settings(booth_id: int) -> dict:
    try:
        svc = get_settings_service()
        config = await svc.get(booth_id)
        meta = await svc.metadata(booth_id)
        return {"config": config.model_dump(mode="python"), "metadata": meta}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/{booth_id}/settings")
async def update_settings(booth_id: int, payload: AppConfig) -> dict:
    try:
        svc = get_settings_service()
        config = await svc.save(booth_id, payload)
        meta = await svc.metadata(booth_id)
        return {
            "config": config.model_dump(mode="python"),
            "metadata": meta,
            "message": "Настройки сохранены",
        }
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


# ── Parking ───────────────────────────────────────────────────────────────────

@router.get("/{booth_id}/parking/status")
async def parking_status(booth_id: int) -> dict:
    try:
        return await get_parking_service().fetch_status(booth_id)
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


# ── Media ─────────────────────────────────────────────────────────────────────

@router.get("/{booth_id}/media/items")
async def media_items(booth_id: int) -> dict:
    return {"items": get_media_service().list_items(booth_id)}


@router.post("/{booth_id}/media/upload")
async def media_upload(booth_id: int, file: UploadFile = File(...)) -> dict:
    try:
        get_media_service().save_file(booth_id, file.filename or "", await file.read())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"message": "Файл загружен", "name": file.filename}


@router.delete("/{booth_id}/media/file/{relative_path:path}")
async def media_delete(booth_id: int, relative_path: str) -> dict:
    try:
        get_media_service().delete_file(booth_id, unquote(relative_path))
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
