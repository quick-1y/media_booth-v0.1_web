from __future__ import annotations
import json
from app.db import get_pool
from app.schemas.config import AppConfig


class BoothsService:
    async def list_booths(self) -> list[dict]:
        pool = get_pool()
        rows = await pool.fetch(
            "SELECT id, name, created_at, updated_at FROM booths ORDER BY id"
        )
        return [
            {
                "id": r["id"],
                "name": r["name"],
                "created_at": r["created_at"].isoformat(),
                "updated_at": r["updated_at"].isoformat(),
            }
            for r in rows
        ]

    async def create_booth(self, name: str) -> dict:
        pool = get_pool()
        default = json.dumps(AppConfig().model_dump(mode="python"))
        row = await pool.fetchrow(
            "INSERT INTO booths (name, settings) VALUES ($1, $2::jsonb)"
            " RETURNING id, name, created_at, updated_at",
            name.strip(),
            default,
        )
        return {
            "id": row["id"],
            "name": row["name"],
            "created_at": row["created_at"].isoformat(),
            "updated_at": row["updated_at"].isoformat(),
        }

    async def delete_booth(self, booth_id: int) -> None:
        pool = get_pool()
        result = await pool.execute("DELETE FROM booths WHERE id = $1", booth_id)
        if result == "DELETE 0":
            raise ValueError(f"Стенд {booth_id} не найден")

    async def exists(self, booth_id: int) -> bool:
        pool = get_pool()
        row = await pool.fetchrow("SELECT 1 FROM booths WHERE id = $1", booth_id)
        return row is not None
