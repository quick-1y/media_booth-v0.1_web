from __future__ import annotations
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Callable
import httpx

_TIMEOUT = 10
_REFRESH_SECONDS = 15
_VERIFY_TLS = True


class ParkingService:
    def __init__(self, settings_factory: Callable) -> None:
        self._settings_factory = settings_factory
        self._locks: dict[int, asyncio.Lock] = {}
        self._cached: dict[int, dict] = {}
        self._until: dict[int, datetime] = {}

    def _lock(self, booth_id: int) -> asyncio.Lock:
        if booth_id not in self._locks:
            self._locks[booth_id] = asyncio.Lock()
        return self._locks[booth_id]

    @staticmethod
    def _build_url(server: str, path: str, token: str) -> str:
        if not server:
            return ""
        url = server.rstrip("/") + "/" + path.lstrip("/")
        if token:
            sep = "&" if "?" in url else "?"
            url += f"{sep}token={token}"
        return url

    @staticmethod
    def _normalize(payload: dict) -> dict:
        levels_out = []
        total = 0
        for idx, item in enumerate(payload.get("levels", []), start=1):
            if not isinstance(item, dict):
                continue
            free = item.get("free")
            try:
                free_int = None if free is None else int(free)
            except Exception:
                free_int = None
            if free_int is not None:
                total += free_int
            levels_out.append({
                "map_id": item.get("map_id"),
                "label": item.get("label") or f"Уровень {idx}",
                "free": free_int,
                "error": item.get("error"),
            })
        return {
            "success": bool(payload.get("success", True)),
            "generated_at": payload.get("generated_at"),
            "levels": levels_out,
            "total_free": payload.get("total_free", total),
            "partial": bool(payload.get("partial", False)),
            "error": payload.get("error"),
        }

    async def _fetch_json(self, url: str) -> dict:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(_TIMEOUT), verify=_VERIFY_TLS, follow_redirects=True
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()

    async def fetch_status(self, booth_id: int, force: bool = False) -> dict:
        config = await self._settings_factory().get(booth_id)
        parser = config.parking.parser
        url = self._build_url(parser.server, parser.path, parser.token)
        if not url:
            return {
                "success": False, "levels": [], "total_free": 0,
                "partial": False, "error": "Парсер не настроен",
            }
        async with self._lock(booth_id):
            now = datetime.now(timezone.utc)
            if (
                not force
                and booth_id in self._cached
                and booth_id in self._until
                and now < self._until[booth_id]
            ):
                return {**self._cached[booth_id], "cached": True}
            try:
                payload = await self._fetch_json(url)
                data = self._normalize(payload)
                data["fetched_at"] = now.isoformat()
                data["source_url"] = url
                data["cached"] = False
                self._cached[booth_id] = data
                self._until[booth_id] = now + timedelta(seconds=_REFRESH_SECONDS)
                return data
            except Exception as exc:
                if booth_id in self._cached:
                    return {
                        **self._cached[booth_id],
                        "success": False,
                        "stale": True,
                        "cached": True,
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                return {
                    "success": False, "levels": [], "total_free": 0,
                    "partial": False, "error": f"{type(exc).__name__}: {exc}",
                }

    async def test_parser(self, server: str, path: str, token: str) -> dict:
        url = self._build_url(server, path, token)
        if not url:
            raise ValueError("Не указан адрес сервера")
        payload = await self._fetch_json(url)
        data = self._normalize(payload)
        data["tested_url"] = url
        return data
