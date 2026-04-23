from urllib.parse import unquote
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from app.services.deps import get_media_service

router = APIRouter()


@router.get("/items")
async def media_items() -> dict:
    return {"items": get_media_service().list_items()}


@router.post("/upload")
async def media_upload(file: UploadFile = File(...)) -> dict:
    service = get_media_service()
    try:
        data = await file.read()
        service.save_file(file.filename or "", data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"message": "Файл загружен", "name": file.filename}


@router.delete("/file/{relative_path:path}")
async def media_delete(relative_path: str) -> dict:
    service = get_media_service()
    try:
        service.delete_file(unquote(relative_path))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"message": "Файл удалён"}


@router.get("/file/{relative_path:path}")
async def media_file_api(relative_path: str) -> FileResponse:
    try:
        path = get_media_service().get_file_path(unquote(relative_path))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="Файл не найден")
    return FileResponse(path)
