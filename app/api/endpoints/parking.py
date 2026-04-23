from fastapi import APIRouter, HTTPException
from app.schemas.config import ParserTestRequest
from app.services.deps import get_parking_service

router = APIRouter()


@router.get("/status")
async def parking_status() -> dict:
    return await get_parking_service().fetch_status(force=False)


@router.post("/test")
async def parking_test(payload: ParserTestRequest) -> dict:
    if not payload.server.strip():
        raise HTTPException(status_code=400, detail="Адрес сервера не указан")
    try:
        return await get_parking_service().test_parser(
            payload.server.strip(), payload.path.strip(), payload.token.strip()
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"{type(exc).__name__}: {exc}") from exc
