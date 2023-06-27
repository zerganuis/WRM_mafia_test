import asyncio

import aiosqlite

from mafia_bot import config


async def get_db() -> aiosqlite.Connection:
    if not getattr(get_db, "db", None):
        db = await aiosqlite.connect(config.SQLITE_DB_FILE)
        get_db.db = db
    return get_db.db


def close_db() -> None:
    asyncio.run(_async_close_db())


async def _async_close_db() -> None:
    await (await get_db()).close()
