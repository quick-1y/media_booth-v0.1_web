from __future__ import annotations
from pathlib import Path
from typing import Callable
from urllib.parse import quote
from app.schemas.config import AppConfig


class MediaService:
    def __init__(self, settings_factory: Callable[[], object]) -> None:
        self._settings_factory = settings_factory

    def _settings(self) -> AppConfig:
        return self._settings_factory().get()

    def _root(self) -> Path:
        return Path(self._settings().media.ads_path)

    def _allowed(self) -> set[str]:
        return {item.lower() for item in self._settings().media.allowed_extensions}

    def _safe_path(self, relative_path: str) -> Path:
        base = self._root().resolve()
        target = (base / relative_path).resolve()
        if target != base and base not in target.parents:
            raise ValueError("Недопустимый путь к медиафайлу")
        return target

    def list_items(self) -> list[dict]:
        root = self._root()
        root.mkdir(parents=True, exist_ok=True)
        allowed = self._allowed()
        items = []
        for p in sorted(root.iterdir(), key=lambda x: x.name.lower()):
            if not p.is_file() or p.suffix.lower() not in allowed:
                continue
            items.append({
                "name": p.name,
                "url": f"/media/{quote(p.name)}",
                "type": "video" if p.suffix.lower() in {".mp4", ".webm", ".ogg"} else "image",
                "size_bytes": p.stat().st_size,
            })
        return items

    def save_file(self, filename: str, data: bytes) -> None:
        if Path(filename).suffix.lower() not in self._allowed():
            raise ValueError("Недопустимый тип файла")
        root = self._root()
        root.mkdir(parents=True, exist_ok=True)
        self._safe_path(filename).write_bytes(data)

    def delete_file(self, filename: str) -> None:
        path = self._safe_path(filename)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError("Файл не найден")
        path.unlink()

    def get_file_path(self, relative_path: str) -> Path:
        return self._safe_path(relative_path)
