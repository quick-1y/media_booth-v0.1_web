from urllib.parse import unquote
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from app.services.deps import get_media_service
router = APIRouter()
templates = Jinja2Templates(directory='app/web/templates')

@router.get('/')
async def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

@router.get('/media/{relative_path:path}')
async def media_file(relative_path: str) -> FileResponse:
    try:
        path = get_media_service().get_file_path(unquote(relative_path))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail='Файл не найден')
    return FileResponse(path)
