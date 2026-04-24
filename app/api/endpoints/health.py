from datetime import datetime, timezone
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def healthcheck() -> dict:
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}
