from __future__ import annotations
import json
from app.db import get_pool
from app.schemas.config import AppConfig


class BoothSettingsService:
    async def get(self, booth_id: int) -> AppConfig:
        pool = get_pool()
        row = await pool.fetchrow("SELECT settings FROM booths WHERE id = $1", booth_id)
        if not row:
            raise ValueError(f"Стенд {booth_id} не найден")
        data = row["settings"]
        if isinstance(data, str):
            data = json.loads(data)
        return AppConfig.model_validate(data)

    async def save(self, booth_id: int, config: AppConfig) -> AppConfig:
        pool = get_pool()
        payload = config.model_dump(mode="python")
        result = await pool.execute(
            "UPDATE booths SET settings = $1::jsonb, updated_at = NOW() WHERE id = $2",
            json.dumps(payload),
            booth_id,
        )
        if result == "UPDATE 0":
            raise ValueError(f"Стенд {booth_id} не найден")
        return config

    async def metadata(self, booth_id: int) -> dict:
        pool = get_pool()
        row = await pool.fetchrow(
            "SELECT created_at, updated_at FROM booths WHERE id = $1", booth_id
        )
        if not row:
            return {"booth_id": booth_id, "loaded_at": None, "saved_at": None}
        return {
            "booth_id": booth_id,
            "loaded_at": row["created_at"].isoformat(),
            "saved_at": row["updated_at"].isoformat(),
        }
