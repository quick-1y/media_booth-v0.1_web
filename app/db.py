from __future__ import annotations
import asyncio
import json
import os
import asyncpg

_pool: asyncpg.Pool | None = None


async def _set_codecs(conn: asyncpg.Connection) -> None:
    await conn.set_type_codec(
        "jsonb",
        encoder=json.dumps,
        decoder=json.loads,
        schema="pg_catalog",
    )


async def init_pool() -> None:
    global _pool
    url = os.getenv("DATABASE_URL", "postgresql://booth:booth@postgres:5432/booth")
    for attempt in range(1, 11):
        try:
            _pool = await asyncpg.create_pool(
                url, min_size=2, max_size=10, init=_set_codecs
            )
            await _run_migrations(_pool)
            return
        except Exception:
            if attempt == 10:
                raise
            await asyncio.sleep(2 * attempt)


async def close_pool() -> None:
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("Database pool not initialized")
    return _pool


async def _run_migrations(pool: asyncpg.Pool) -> None:
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS booths (
                id               SERIAL PRIMARY KEY,
                name             VARCHAR(100) NOT NULL,
                settings         JSONB NOT NULL DEFAULT '{}',
                created_at       TIMESTAMPTZ DEFAULT NOW(),
                updated_at       TIMESTAMPTZ DEFAULT NOW(),
                media_updated_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        await conn.execute("""
            ALTER TABLE booths
            ADD COLUMN IF NOT EXISTS media_updated_at TIMESTAMPTZ DEFAULT NOW()
        """)
