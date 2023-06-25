from dataclasses import dataclass
from datetime import datetime

import aiosqlite

import config

@dataclass
class Event:
    telegram_id: int
    name: str
    date: datetime
    place: str
    members: list[int]
    ordering: int

async def get_all_events() -> list[Event]:
    async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
        async with db.execute("SELECT * FROM event") as cursor:
            async for row in cursor:
                print(row)
