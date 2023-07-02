from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from typing import LiteralString

from mafia_bot import config
from mafia_bot.db import fetch_all, fetch_one

@dataclass
class Event:
    id: int
    name: str
    datetime: datetime
    place: str
    host_id: int
    description: LiteralString = ""
    userlist: Iterable | None = None

Page = Iterable[Event]

async def get_eventlist() -> Iterable[Page]:
    sql = f"""{_get_events_base_sql()}
              where e.datetime > datetime('now')
              order by e.datetime"""
    events = await _get_eventlist_from_db(sql)
    return _group_events_by_pages(events)

def _group_events_by_pages(events: Iterable[Event]) -> Iterable[Page]:
    pagelen=config.EVENTLIST_PAGE_LENGTH
    eventlist = []
    for i in range(len(events) // pagelen + len(events) % pagelen):
        eventlist.append([])
        for j in range(pagelen):
            event_index = i * pagelen + j
            if event_index >= len(events):
                break
            eventlist[-1].append(events[event_index])
    return eventlist

def _get_events_base_sql(select_param: LiteralString | None = None) -> LiteralString:
    return f"""SELECT
                   e.id as id,
                   e.name as name,
                   e.place as place,
                   e.host_id as host_id,
                   {select_param + "," if select_param else ""}
                   e.datetime as datetime
               FROM event e"""

async def _get_eventlist_from_db(sql: LiteralString) -> Iterable[Event]:
    events_raw = await fetch_all(sql)
    return [
        Event(
            id=event["id"],
            name=event["name"],
            place=event["place"],
            datetime=event["datetime"],
            host_id=event["host_id"]
        )
        for event in events_raw
    ]

async def _get_event_from_db(sql: LiteralString) -> Event:
    event = await fetch_one(sql)
    return Event(
        id=event["id"],
        name=event["name"],
        place=event["place"],
        datetime=event["datetime"],
        host_id=event["host_id"],
        # description=event["description"]
    )

async def get_event(event_id: int) -> Event:
    sql = f"""{_get_events_base_sql()}
              where e.id = {event_id}"""
    event = await _get_event_from_db(sql)
    return event


async def update_event_parameter(param_name: str, param_value: str, event_id: int):
    sql = f"""UPDATE event
        SET {param_name} = '{param_value}'
        where id = {event_id}
    """
    await fetch_one(sql)


async def insert_event_id(event_id: int):
    sql_user = f"""INSERT INTO event values
    ({event_id}, '', datetime('now'), '', null)"""
    sql_user_reg = f"""INSERT INTO event_registration values ({event_id})"""
    await fetch_one(sql_user)
    await fetch_one(sql_user_reg)


async def delete_event(event_id: int):
    sql_user = f"""DELETE from event where id = {event_id}"""
    await fetch_one(sql_user)


async def delete_event_registration(event_id: int):
    sql_user_reg = f"""DELETE from event_registration where id = {event_id}"""
    await fetch_one(sql_user_reg)


# sql_reqest = f"""select max(id) as max_id from event"""
# max_event_id_dict = await fetch_one(sql_reqest)
# max_event_id = max_event_id_dict['max_id']
# print(max_event_id)
# next_event_id = max_event_id + 1