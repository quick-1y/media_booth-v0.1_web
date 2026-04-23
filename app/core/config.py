from __future__ import annotations
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

@dataclass(slots=True)
class RuntimeSettings:
    config_path: Path
    log_level: str = "info"

@lru_cache(maxsize=1)
def get_runtime_settings() -> RuntimeSettings:
    return RuntimeSettings(
        config_path=Path(os.getenv("APP_CONFIG_PATH", "/app/config/settings.yaml")),
        log_level=os.getenv("APP_LOG_LEVEL", "info").lower(),
    )
