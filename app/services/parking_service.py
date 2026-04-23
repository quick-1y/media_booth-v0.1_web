from __future__ import annotations
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Callable
import httpx
from app.schemas.config import AppConfig

_TIMEOUT = 10
_REFRESH_SECONDS = 15
_VERIFY_TLS = True


class ParkingService:
    def __init__(self, settings_factory: Callable[[], object]) -> None:
        self._settings_factory = settings_factory
        self._cache_lock = asyncio.Lock()
        self._cached_payload: dict | None = None
        self._cached_until: datetime | None = None

    def _settings(self) -> AppConfig:
        return self._settings_factory().get()

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

    async def fetch_status(self, force: bool = False) -> dict:
        config = self._settings()
        parser = config.parking.parser
        url = self._build_url(parser.server, parser.path, parser.token)
        if not url:
            return {"success": False, "levels": [], "total_free": 0, "partial": False, "error": "Парсер не настроен"}
        async with self._cache_lock:
            now = datetime.now(timezone.utc)
            if (
                not force
                and self._cached_payload is not None
                and self._cached_until is not None
                and now < self._cached_until
            ):
                return {**self._cached_payload, "cached": True}
            try:
                payload = await self._fetch_json(url)
                data = self._normalize(payload)
                data["fetched_at"] = now.isoformat()
                data["source_url"] = url
                data["cached"] = False
                self._cached_payload = data
                self._cached_until = now + timedelta(seconds=_REFRESH_SECONDS)
                return data
            except Exception as exc:
                if self._cached_payload is not None:
                    return {
                        **self._cached_payload,
                        "success": False,
                        "stale": True,
                        "cached": True,
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                return {
                    "success": False,
                    "levels": [],
                    "total_free": 0,
                    "partial": False,
                    "error": f"{type(exc).__name__}: {exc}",
                }

    async def test_parser(self, server: str, path: str, token: str) -> dict:
        url = self._build_url(server, path, token)
        if not url:
            raise ValueError("Не указан адрес сервера")
        payload = await self._fetch_json(url)
        data = self._normalize(payload)
        data["tested_url"] = url
        return data
