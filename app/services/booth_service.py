from __future__ import annotations
import json
from app.db import get_pool
from app.schemas.config import AppConfig


class BoothService:
    async def list(self) -> list[dict]:
        rows = await get_pool().fetch(
            "SELECT id, name, created_at, updated_at FROM booths ORDER BY id"
        )
        return [_row(r) for r in rows]

    async def create(self, name: str) -> dict:
        default = json.dumps(AppConfig().model_dump(mode="python"))
        row = await get_pool().fetchrow(
            "INSERT INTO booths (name, settings) VALUES ($1, $2::jsonb)"
            " RETURNING id, name, created_at, updated_at",
            name,
            default,
        )
        return _row(row)

    async def rename(self, booth_id: int, name: str) -> None:
        result = await get_pool().execute(
            "UPDATE booths SET name = $1, updated_at = NOW() WHERE id = $2",
            name,
            booth_id,
        )
        if result == "UPDATE 0":
            raise ValueError(f"Стенд {booth_id} не найден")

    async def delete(self, booth_id: int) -> None:
        result = await get_pool().execute(
            "DELETE FROM booths WHERE id = $1", booth_id
        )
        if result == "DELETE 0":
            raise ValueError(f"Стенд {booth_id} не найден")


def _row(r) -> dict:
    return {
        "id": r["id"],
        "name": r["name"],
        "created_at": r["created_at"].isoformat(),
        "updated_at": r["updated_at"].isoformat(),
    }
