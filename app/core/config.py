from __future__ import annotations
import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path


@dataclass(slots=True)
class RuntimeSettings:
    log_level: str = "info"
    data_dir: Path = field(default_factory=lambda: Path("/data"))
    db_url: str = "postgresql://booth:booth@postgres:5432/booth"


@lru_cache(maxsize=1)
def get_runtime_settings() -> RuntimeSettings:
    return RuntimeSettings(
        log_level=os.getenv("APP_LOG_LEVEL", "info").lower(),
        data_dir=Path(os.getenv("APP_DATA_DIR", "/data")),
        db_url=os.getenv("DATABASE_URL", "postgresql://booth:booth@postgres:5432/booth"),
    )
