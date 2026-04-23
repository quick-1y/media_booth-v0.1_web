from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
import yaml
from app.schemas.config import AppConfig

@dataclass(slots=True)
class SettingsMetadata:
    config_path: str
    loaded_at: str
    saved_at: str | None = None

class SettingsService:
    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path
        self._lock = Lock()
        self._config = AppConfig()
        self._raw_yaml = ""
        self._loaded_at = self._now_iso()
        self._saved_at = None
        self._ensure_exists()
        self.reload()

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _ensure_exists(self) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.config_path.exists():
            self.config_path.write_text(yaml.safe_dump(AppConfig().model_dump(mode="python"), allow_unicode=True, sort_keys=False), encoding="utf-8")

    def reload(self) -> AppConfig:
        with self._lock:
            raw = self.config_path.read_text(encoding="utf-8")
            parsed = yaml.safe_load(raw) or {}
            self._config = AppConfig.model_validate(parsed)
            self._raw_yaml = raw
            self._loaded_at = self._now_iso()
            return AppConfig.model_validate(self._config.model_dump(mode="python"))

    def get(self) -> AppConfig:
        with self._lock:
            return AppConfig.model_validate(self._config.model_dump(mode="python"))

    def save(self, config: AppConfig) -> AppConfig:
        with self._lock:
            payload = config.model_dump(mode="python")
            raw = yaml.safe_dump(payload, allow_unicode=True, sort_keys=False)
            self.config_path.write_text(raw, encoding="utf-8")
            self._config = AppConfig.model_validate(payload)
            self._raw_yaml = raw
            self._saved_at = self._now_iso()
            self._loaded_at = self._saved_at
            return AppConfig.model_validate(self._config.model_dump(mode="python"))

    def raw_yaml(self) -> str:
        with self._lock:
            return self._raw_yaml

    def metadata(self) -> SettingsMetadata:
        with self._lock:
            return SettingsMetadata(str(self.config_path), self._loaded_at, self._saved_at)
