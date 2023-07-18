from collections.abc import Iterable
from dataclasses import dataclass
import datetime
import enum

from telegram import Update
from telegram.ext import ContextTypes

from mafia_bot import config
from mafia_bot.db import fetch_all, fetch_one, execute


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
    hasPhoto: bool
    access_level: AccessLevel
    total_score: int | None = None

Page = Iterable[User]

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


def validate_user(function_access_level: AccessLevel = AccessLevel.WALKER):
    def inner(handler):
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user_id = update.effective_user.id
            user = await get_user_by_id(user_id)
            if user:
                user_access_level = user.access_level
                constant_admin_id_list = await get_constant_admin_list()
                if user_id in constant_admin_id_list:
                    user_access_level = AccessLevel.ADMIN
            else:
                user_access_level = AccessLevel.WALKER
            if function_access_level == AccessLevel.WALKER:
                return await handler(update, context, user_access_level)
            else:
                userlist = await get_userlist_by_access_level(function_access_level)
                if not user_id in userlist:
                    return
                return await handler(update, context, user_access_level)
        return wrapper
    return inner


async def get_top_users(period: datetime.timedelta = 0, limit = config.TOP_PAGE_LENGTH) -> Iterable[User]:
    select_param = """iif(tt.total_score is null, 0.0, tt.total_score) as total_score"""
    sql = f"""{_get_users_base_sql(select_param)}
            LEFT JOIN (
                select
                    total(s.score) as total_score,
                    s.user_id as user_id
                from statistic s
                {f'''LEFT JOIN event e ON e.id=s.event_id
                WHERE
                    e.datetime >  (datetime('now') - datetime({period.total_seconds()}, 'unixepoch'))''' if period else " "}
                group by s.user_id
            ) tt on tt.user_id = id
            order by total_score desc
            limit {limit}"""
    users = await _get_userlist_from_db(sql)
    return users


async def get_user_statistic(user_id: int, period: datetime.timedelta = 0) -> dict:
    sql = f"""select
                iif(total(s.score) is null, 0.0, total(s.score)) as total_score,
                count(s.isWinner = True) as win_count,
                count (*) as event_count,
                count(s.isWinner = True) / count(*) * 100 as win_rate
            from user u
            LEFT JOIN statistic s on s.user_id = u.telegram_id
            left join event e on e.id = s.event_id
            where
                u.telegram_id = {user_id}
                {f'''and e.datetime >  (datetime('now') - datetime({period.total_seconds()}, 'unixepoch'))''' if period else " "}"""
    stats = await fetch_one(sql)
    if not stats["win_rate"]:
        stats["win_rate"] = 0
    return stats


async def get_userlist_by_access_level(access_level: AccessLevel) -> Iterable[User]:
    sql = f"""  SELECT
                    telegram_id as user_id
                FROM user
                WHERE access_level >= {access_level.value}"""
    user_ids_raw = await fetch_all(sql)
    user_id_list = [user_id_raw["user_id"] for user_id_raw in user_ids_raw]
    if access_level == AccessLevel.ADMIN:
        constant_admin_id_list = await get_constant_admin_list()
        user_id_list = user_id_list + constant_admin_id_list
    return set(user_id_list)

async def get_constant_admin_list():
    sql = f"""  select
                a.telegram_id as user_id
                from admin a
                inner join user u on u.telegram_id = a.telegram_id;"""
    admin_ids_raw = await fetch_all(sql)
    admin_id_list = [user_id_raw["user_id"] for user_id_raw in admin_ids_raw]
    return admin_id_list


async def get_userlist() -> Iterable[Page]:
    sql = f"""{_get_users_base_sql()}"""
    users = await _get_userlist_from_db(sql)
    return _group_users_by_pages(users)


def _group_users_by_pages(users: Iterable[User]) -> Iterable[Page]:
    pagelen=config.USERLIST_PAGE_LENGTH
    userlist = []
    for i in range(len(users) // pagelen + int(bool(len(users) % pagelen))):
        userlist.append([])
        for j in range(pagelen):
            user_index = i * pagelen + j
            if user_index >= len(users):
                break
            userlist[-1].append(users[user_index])
    return userlist

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


def _get_users_base_sql(select_param: str | None = None) -> str:
    return f"""SELECT
                   u.telegram_id as id,
                   u.name as name,
                   u.nickname as nickname,
                   u.city as city,
                   u.hasPhoto as hasPhoto,
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
            hasPhoto=user["hasPhoto"],
            access_level=_get_access_level(user["access_level"]),
            total_score=user.get("total_score", None)
        )
        for user in users_raw
    ]


async def _get_user_from_db(sql: str) -> User:
    user = await fetch_one(sql)
    if user:
        return User(
                id=user["id"],
                name=user["name"],
                nickname=user["nickname"],
                city=user["city"],
                hasPhoto=user["hasPhoto"],
                access_level=_get_access_level(user["access_level"]),
                total_score=user.get("total_score", None)
            )
    return None


async def update_user_parameter(param_name: str, param_value: str, user_id: int):
    sql = f"""UPDATE user
        SET {param_name} = {f"{param_value}" if param_name == "hasPhoto" else f"'{param_value}'"}
        where telegram_id = {user_id}
    """
    await execute(sql)


async def update_user_access_level(access_level: int, user_id: int):
    sql = f"""UPDATE user
        SET access_level = {access_level}
        where telegram_id = {user_id}
    """
    await execute(sql)


async def insert_user_id(telegram_id: int):
    sql_user = f"""INSERT INTO user values
    ({telegram_id}, '', '', '', '', 1)"""
    sql_user_reg = f"""INSERT INTO user_registration values ({telegram_id})"""
    await execute(sql_user)
    await execute(sql_user_reg)


async def delete_user(telegram_id: int):
    sql_user = f"""DELETE from user where telegram_id = {telegram_id};"""
    await execute(sql_user)


async def delete_user_registration(telegram_id: int):
    sql_user_reg = f"""DELETE from user_registration where telegram_id = {telegram_id}"""
    await execute(sql_user_reg)


async def edit_statistic_is_winner(user_id: int, event_id: int, isWinner: bool):
    sql = f"""  update statistic
                set isWinner = {'true' if isWinner else 'false'}
                where user_id = {user_id} and event_id = {event_id}"""
    await execute(sql)


async def edit_statistic_score(user_id: int, event_id: int, score: int):
    sql = f"""  update statistic
                set score = {score}
                where user_id = {user_id} and event_id = {event_id}"""
    await execute(sql)


async def insert_edit_statistic(editor_id: int, user_id: int, event_id: int):
    sql = f"""INSERT INTO statistic_edit values ({editor_id}, {user_id}, {event_id})"""
    await execute(sql)


async def delete_edit_statistic(editor_id: int):
    sql = f"""DELETE from statistic_edit where editor_id = {editor_id}"""
    await execute(sql)


async def get_edit_statistic(editor_id: int) -> dict[str, int]:
    sql = f"""select * from statistic_edit where editor_id = {editor_id}"""
    response = await fetch_one(sql)
    return response


def get_user_id_by_telegram_nick(telegram_nick: str) -> int:
    return
