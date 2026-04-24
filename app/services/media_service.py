from __future__ import annotations
from pathlib import Path
from urllib.parse import quote
from app.config import get_runtime_settings

_ALLOWED = frozenset({".jpg", ".jpeg", ".png", ".webp", ".gif", ".mp4", ".webm", ".ogg"})
_VIDEO = frozenset({".mp4", ".webm", ".ogg"})


class MediaService:
    def _root(self, booth_id: int) -> Path:
        return get_runtime_settings().data_dir / "booths" / str(booth_id)

    def _safe_path(self, booth_id: int, relative_path: str) -> Path:
        base = self._root(booth_id).resolve()
        target = (base / relative_path).resolve()
        if target != base and base not in target.parents:
            raise ValueError("Недопустимый путь к медиафайлу")
        return target

    def list_items(self, booth_id: int) -> list[dict]:
        root = self._root(booth_id)
        root.mkdir(parents=True, exist_ok=True)
        items = []
        for p in sorted(root.iterdir(), key=lambda x: x.name.lower()):
            if not p.is_file() or p.suffix.lower() not in _ALLOWED:
                continue
            items.append({
                "name": p.name,
                "url": f"/api/booths/{booth_id}/media/file/{quote(p.name)}",
                "type": "video" if p.suffix.lower() in _VIDEO else "image",
                "size_bytes": p.stat().st_size,
            })
        return items

    def save_file(self, booth_id: int, filename: str, data: bytes) -> None:
        if Path(filename).suffix.lower() not in _ALLOWED:
            raise ValueError("Недопустимый тип файла")
        root = self._root(booth_id)
        root.mkdir(parents=True, exist_ok=True)
        self._safe_path(booth_id, filename).write_bytes(data)

    def delete_file(self, booth_id: int, filename: str) -> None:
        path = self._safe_path(booth_id, filename)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError("Файл не найден")
        path.unlink()

    def get_file_path(self, booth_id: int, relative_path: str) -> Path:
        return self._safe_path(booth_id, relative_path)
