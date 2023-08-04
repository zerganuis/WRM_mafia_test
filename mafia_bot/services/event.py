from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime

from mafia_bot import config
from mafia_bot.db import fetch_one, execute


@dataclass
class Event:
    id: int
    name: str
    datetime: datetime
    place: str = ''
    cost: str = ''
    description: str = ''
    host_id: int | None = None
    picture: str = config.BASE_EVENT_PHOTO
    event_type: str | None = None
    userlist: Iterable | None = None


### Getting Event

def _event_base_sql(select_param: str | None = None) -> str:
    return f"""
        SELECT
            {select_param + "," if select_param else ""}
            event.id as id,
            event.name as name,
            event.datetime as datetime,
            event.place as place,
            event.cost as cost,
            event.description as description,
            event.host_id as host_id,
            event.picture as picture,
            event.type as event_type
        FROM event
    """


async def _get_event_from_db(sql: str) -> Event:
    event = await fetch_one(sql)
    if event.get("picture", None):
        picture = event["picture"]
        try:
            open(event["picture"], 'rb')
        except Exception:
            picture = config.BASE_EVENT_PHOTO
    else:
        picture = config.BASE_EVENT_PHOTO
    return Event(
        id=event["id"],
        name=event["name"],
        place=event["place"],
        datetime=datetime.strptime(event["datetime"], rf"%Y-%m-%d %H:%M:%S"),
        host_id=event["host_id"],
        cost=event["cost"],
        description=event["description"],
        picture=picture,
        event_type=event["event_type"]
    )


async def get_event_by_id(event_id: int) -> Event:
    sql = f"""
        {_event_base_sql()}
        WHERE event.id = {event_id}
    """
    event = await _get_event_from_db(sql)
    return event


### Updating and Inserting Events' Data

async def get_max_event_id() -> int:
    sql = f"""select max(id) as max_id from event"""
    response = await fetch_one(sql)
    return response['max_id']


async def update_event_parameter(event_id: int, param_name: str, param_value):
    match param_name:
        case 'name'|'place'|'cost'|'description'|'picture'|'type':
            param_value = f"'{param_value}'"
        case 'host_id':
            param_value = str(param_value)
        case 'datetime':
            pass
        case _:
            raise ValueError(f"Invalid parameter name plased into update event function: {param_name}")
    sql = f"""
        UPDATE event
        SET {param_name} = {param_value}
        WHERE id = {event_id}
    """
    await execute(sql)


async def insert_event_id(user_id: int, event_id: int):
    sql_event = f"""
        INSERT INTO event VALUES
        ({event_id}, '', datetime(0), '', '', '', null, '{config.BASE_EVENT_PHOTO}', '')
    """
    sql_event_edit = f"""INSERT INTO event_edit VALUES ({user_id}, {event_id})"""
    await execute(sql_event)
    await execute(sql_event_edit)


async def delete_event(event_id: int):
    sql = f"""DELETE FROM event WHERE id = {event_id}"""
    await execute(sql)


async def delete_event_edit(event_id: int):
    sql = f"""DELETE FROM event_edit WHERE event_id = {event_id}"""
    await execute(sql)


async def insert_event_edit(user_id: int, event_id: int):
    sql = f"""INSERT INTO event_edit VALUES ({user_id}, {event_id})"""
    await execute(sql)


async def sign_up(user_id: int, event_id: int):
    sql = f"""INSERT INTO statistic (user_id, event_id) VALUES ({user_id}, {event_id})"""
    await execute(sql)


async def sign_out(user_id: int, event_id: int):
    sql = f"""DELETE FROM statistic WHERE user_id = {user_id} AND event_id = {event_id}"""
    await execute(sql)


async def is_signed_up(user_id: int, event_id: int) -> bool:
    sql = f"""SELECT * FROM statistic WHERE user_id = {user_id} AND event_id = {event_id}"""
    res = await fetch_one(sql)
    return bool(res)


async def get_edit_event_id(user_id: int) -> int:
    sql = f"""SELECT event_id FROM event_edit WHERE editor_id = {user_id}"""
    response = await fetch_one(sql)
    return response['event_id']


def format_datetime_to_db(text: str) -> str:
    dt = datetime.strptime(text, config.DATETIME_FORMAT)
    dt_to_sql = dt.strftime(rf"%Y-%m-%d %H:%M:%S")
    return dt_to_sql
