from collections.abc import Iterable
from dataclasses import dataclass
import datetime
from typing import LiteralString
import enum

from telegram import Update
from telegram.ext import ContextTypes

from mafia_bot import config
from mafia_bot.db import fetch_all, fetch_one


class AccessLevel(enum.Enum):
    WALKER: 'AccessLevel' = 0
    USER: 'AccessLevel' = 1
    ADMIN: 'AccessLevel' = 2


@dataclass
class User:
    id: int
    name: str
    nickname: str
    city: str
    photo_link: str
    access_level: AccessLevel
    total_score: int | None = None


def _get_access_level(access_level_id: int) -> AccessLevel:
    match access_level_id:
        case 0:
            return AccessLevel.WALKER
        case 1:
            return AccessLevel.USER
        case 2:
            return AccessLevel.ADMIN
        case _:
            raise ValueError(f"Unsupported access_level_id value: {access_level_id}")


def validate_user(access_level: AccessLevel = AccessLevel.WALKER):
    def inner(handler):
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user_id = update.effective_user.id
            user = await get_user_by_id(user_id)
            user_access_level = AccessLevel.WALKER if not user else user.access_level
            if access_level == AccessLevel.WALKER:
                return await handler(update, context, user_access_level)
            else:
                userlist = await get_userlist_by_access_level(access_level)
                if not user_id in userlist:
                    return
                return await handler(update, context, user_access_level)
        return wrapper
    return inner


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


async def get_userlist_by_access_level(access_level: AccessLevel) -> Iterable[User]:
    sql = f"""  SELECT
                    telegram_id as user_id
                FROM user
                WHERE access_level >= {access_level.value}"""
    user_ids_raw = await fetch_all(sql)
    user_id_list = [user_id_raw["user_id"] for user_id_raw in user_ids_raw]
    if access_level == AccessLevel.ADMIN:
        sql = f"""  SELECT 
                    telegram_id as user_id
                    FROM admin"""
        admin_ids_raw = await fetch_all(sql)
        admin_id_list = [user_id_raw["user_id"] for user_id_raw in admin_ids_raw]
        user_id_list = user_id_list + admin_id_list
    return set(user_id_list)


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


async def _get_user_from_db(sql: LiteralString) -> User:
    user = await fetch_one(sql)
    if user:
        return User(
                id=user["id"],
                name=user["name"],
                nickname=user["nickname"],
                city=user["city"],
                photo_link=user["photo_link"],
                access_level=_get_access_level(user["access_level"]),
                total_score=user.get("total_score", None)
            )
    return None


async def update_user_parameter(param_name: str, param_value: str, user_id: int):
    sql = f"""UPDATE user
        SET {param_name} = '{param_value}'
        where telegram_id = {user_id}
    """
    await fetch_one(sql)


async def insert_user_id(telegram_id: int):
    sql_user = f"""INSERT INTO user values
    ({telegram_id}, '', '', '', '', 1)"""
    sql_user_reg = f"""INSERT INTO user_registration values ({telegram_id})"""
    await fetch_one(sql_user)
    await fetch_one(sql_user_reg)


async def delete_user(telegram_id: int):
    sql_user = f"""DELETE from user where telegram_id = {telegram_id}"""
    await fetch_one(sql_user)


async def delete_user_registration(telegram_id: int):
    sql_user_reg = f"""DELETE from user_registration where telegram_id = {telegram_id}"""
    await fetch_one(sql_user_reg)

async def edit_statistic_is_winner(user_id: int, event_id: int, isWinner: bool):
    sql = f"""  update statistic
                set isWinner = {'true' if isWinner else 'false'}
                where user_id = {user_id} and event_id = {event_id}"""
    await fetch_one(sql)

async def edit_statistic_score(user_id: int, event_id: int, score: int):
    sql = f"""  update statistic
                set score = {score}
                where user_id = {user_id} and event_id = {event_id}"""
    await fetch_one(sql)


async def insert_edit_statistic(user_id: int, event_id: int):
    sql = f"""INSERT INTO statistic_edit values ({user_id}, {event_id})"""
    await fetch_one(sql)


async def delete_edit_statistic():
    sql = f"""DELETE from statistic_edit"""
    await fetch_one(sql)

async def get_edit_statistic() -> dict[str, int]:
    sql = f"""select * from statistic_edit limit 1"""
    response = await fetch_one(sql)
    return response

def get_user_id_by_telegram_nick(telegram_nick: str) -> int:
    return
