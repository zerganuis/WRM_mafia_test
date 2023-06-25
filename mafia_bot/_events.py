from dataclasses import dataclass
from datetime import datetime

import aiosqlite

import config

@dataclass
class Event:
    id: int
    name: str
    date: datetime
    place: str
    members: list[int]
    ordering: int

def _get_members_id(id_string: str) -> list[int]:
    return list(map(int, id_string.split(",")))

async def get_all_events() -> list[Event]:
    events = []
    async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM event") as cursor:
            async for row in cursor:
                events.append(Event(
                    id=row["id"],
                    name=row["eventname"],
                    date=row["eventdate"],
                    place=row["eventplace"],
                    members=_get_members_id(row["memberlist"]),
                    ordering=row["ordering"]
                ))
    return events
