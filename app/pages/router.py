from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/web/templates")


@router.get("/")
async def management_page(request: Request):
    return templates.TemplateResponse("management.html", {"request": request})


@router.get("/booth/{booth_id}")
async def booth_page(request: Request, booth_id: int):
    return templates.TemplateResponse(
        "index.html", {"request": request, "booth_id": booth_id}
    )
