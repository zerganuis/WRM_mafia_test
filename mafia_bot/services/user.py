from collections.abc import Iterable
from dataclasses import dataclass
import datetime
from typing import LiteralString
import enum

from mafia_bot import config
from mafia_bot.db import fetch_all, fetch_one


class AccessLevel(enum.Enum):
    USER = 0
    ADMIN = 1


@dataclass
class User:
    id: int
    name: str
    nickname: str
    city: str
    photo_link: str
    access_level: AccessLevel
    total_score: int | None = None


async def get_top_users(period: datetime.timedelta = 0):
    select_param = """iif(tt.total_score is null, 0.0, tt.total_score) as total_score"""
    sql = f"""{_get_users_base_sql(select_param)}
            LEFT JOIN (
                select
                    total(s.score) as total_score,
                    s.user_id as user_id
                from statistic s
                {f'''LEFT JOIN event e ON e.id=s.event_id
                WHERE
                    e.datetime >  datetime(unixepoch() - unixepoch(datetime({period.total_seconds()}, 'unixepoch')), 'unixepoch')''' if period else " "}
                group by s.user_id
            ) tt on tt.user_id = id
            order by total_score desc
            limit {config.TOP_PAGE_LENGTH}"""
    users = await _get_userlist_from_db(sql)
    return users


async def get_userlist() -> Iterable[User]:
    sql = f"""{_get_users_base_sql()}"""
    users = await _get_userlist_from_db(sql)
    return users


async def get_userlist_by_event_id(event_id: int) -> Iterable[User]:
    sql = f"""{_get_users_base_sql()[:-11]}
            from statistic s
            left join user u on u.telegram_id = s.user_id
            where s.event_id = {event_id}"""
    users = await _get_userlist_from_db(sql)
    return users


async def get_user_by_id(telegram_id: int) -> User:
    sql = f"""{_get_users_base_sql()}
            WHERE u.telegram_id = {telegram_id}"""
    user = await _get_user_from_db(sql)
    return user


def _get_users_base_sql(select_param: LiteralString | None = None) -> LiteralString:
    return f"""SELECT
                   u.telegram_id as id,
                   u.name as name,
                   u.nickname as nickname,
                   u.city as city,
                   u.photo_link as photo_link,
                   {select_param + "," if select_param else ""}
                   u.access_level as access_level
               FROM user u"""


async def _get_userlist_from_db(sql):
    users_raw = await fetch_all(sql)
    return [
        User(
            id=user["id"],
            name=user["name"],
            nickname=user["nickname"],
            city=user["city"],
            photo_link=user["photo_link"],
            access_level=_get_access_level(user["access_level"]),
            total_score=user.get("total_score", None)
        )
        for user in users_raw
    ]


def _get_access_level(access_level_id: int) -> AccessLevel:
    match access_level_id:
        case 0:
            return AccessLevel.USER
        case 1:
            return AccessLevel.ADMIN
        case _:
            raise ValueError(f"Unsupported access_level_id value: {access_level_id}")


async def _get_user_from_db(sql: LiteralString) -> User:
    user = await fetch_one(sql)
    return User(
            id=user["id"],
            name=user["name"],
            nickname=user["nickname"],
            city=user["city"],
            photo_link=user["photo_link"],
            access_level=_get_access_level(user["access_level"]),
            total_score=user.get("total_score", None)
        )
