from collections.abc import Iterable
from datetime import datetime, timedelta

from mafia_bot import config
from mafia_bot.db import fetch_all
from mafia_bot.services.event import Event
from mafia_bot.services.lists import group_by_pages


async def get_eventlist(
        period: timedelta | None = None
) -> Iterable[Iterable[Event]]:
    """period - переменная, показывающая, насколько в прошлое от текущего времени нужно заглянуть"""
    sql = f"""
        {_eventlist_base_sql()}
        WHERE
            event.datetime > {
                f"datetime('now', '-{period.total_seconds()} seconds')"
                    if period else "0"
            }
        ORDER BY event.datetime
    """
    events = await _get_eventlist_from_db(sql)
    return group_by_pages(events, config.EVENTLIST_PAGE_LENGTH)


async def _get_eventlist_from_db(sql: str) -> Iterable[Event]:
    events_raw = await fetch_all(sql)
    return [
        Event(
            id=event["id"],
            name=event["name"],
            datetime=datetime.strptime(event["datetime"], rf"%Y-%m-%d %H:%M:%S")
        )
        for event in events_raw
    ]


def _eventlist_base_sql(select_param: str | None = None) -> str:
    return f"""
        SELECT
            {select_param + "," if select_param else ""}
            event.id as id,
            event.name as name,
            event.datetime as datetime
        FROM event
    """
