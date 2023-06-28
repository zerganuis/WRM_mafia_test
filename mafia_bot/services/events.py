from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from typing import LiteralString, cast

from mafia_bot import config
from mafia_bot.db import fetch_all

@dataclass
class Event:
    id: int
    name: str
    date: datetime
    place: str
    members: list[int]
    ordering: int


async def get_all_events() -> Iterable[Iterable[Event]]:
    sql = f"""{_get_events_base_sql()}"""
    events = await _get_events_from_db(sql)
    return _group_events_by_pages(events, pagelen=10)

def _group_events_by_pages(events, pagelen=10):
    eventlist = []
    for i in range(len(events) // pagelen + 1):
        eventlist.append(events[i * pagelen : min(len(events) - i * pagelen, (i + 1) * pagelen)])
    return eventlist

def _get_events_base_sql() -> LiteralString:
    return f"""SELECT * FROM event"""

def _get_members_id(id_string: str) -> list[int]:
    return list(map(int, id_string.split(",")))

async def _get_events_from_db(sql: LiteralString) -> list[Event]:
    events_raw = await fetch_all(sql)
    return [
        Event(
            id=event["id"],
            name=event["eventname"],
            date=event["eventdate"],
            place=event["eventplace"],
            members=_get_members_id(event["memberlist"]),
            ordering=event["ordering"]
        )
        for event in events_raw
    ]
