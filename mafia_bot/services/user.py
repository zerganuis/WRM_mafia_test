from dataclasses import dataclass
from datetime import timedelta, datetime

from telegram import Update
from telegram.ext import ContextTypes

from mafia_bot.db import fetch_all, fetch_one, execute
from mafia_bot.services.access import AccessLevel, get_access_level


@dataclass
class User:
    id: int
    name: str = ''
    nickname: str = ''
    city: str = ''
    hasPhoto: bool = False
    birthday: datetime | None = None
    access_level: AccessLevel = AccessLevel.WALKER
    total_score: int | None = None


### User Validation

def validate_user(function_access_level: AccessLevel = AccessLevel.WALKER):
    '''Decorator'''
    def inner(handler):
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user_id = update.effective_user.id
            user = await get_user_by_id(user_id)

            user_access_level = AccessLevel.WALKER
            if user:
                user_access_level = user.access_level
                constant_admin_id_list = await get_constant_admin_list()
                if user_id in constant_admin_id_list:
                    user_access_level = AccessLevel.ADMIN

            if function_access_level == AccessLevel.WALKER:
                return await handler(update, context, user_access_level)

            if user_access_level.value >= function_access_level.value:
                return await handler(update, context, user_access_level)
            return
        return wrapper
    return inner


async def get_constant_admin_list():
    sql = f"""
        SELECT
            admin.user_id as user_id
        FROM admin
        INNER JOIN user ON user.telegram_id = admin.user_id"""
    admin_ids_raw = await fetch_all(sql)
    admin_id_list = [user_id_raw["user_id"] for user_id_raw in admin_ids_raw]
    return admin_id_list


### Getting User's Data


##### Only one function, that not working
def get_user_id_by_telegram_nick(telegram_nick: str) -> int:
    return


async def get_user_statistic(user_id: int, period: timedelta = 0) -> dict:
    sql = f"""
        SELECT
            total(stat.score) as total_score,
            total(stat.game_count) as game_count,
            total(stat.win_count) as win_count,
            total(stat.win_count) / total(stat.game_count) * 100 as win_rate
        FROM user
        LEFT JOIN statistic stat ON stat.user_id = user.telegram_id
        LEFT JOIN event ON event.id = stat.event_id
        WHERE
            user.telegram_id = {user_id}
        AND
            event.datetime < datetime('now') 
        AND
            event.datetime > {
                f"datetime('now', '-{period.total_seconds()} seconds')"
                    if period else "0"
            }
    """
    stats = await fetch_one(sql)
    if not stats["win_rate"]:
        stats["win_rate"] = 0
    return stats


def _get_user_base_sql(select_param: str | None = None) -> str:
    return f"""
        SELECT
            user.telegram_id as id,
            user.name as name,
            user.nickname as nickname,
            user.city as city,
            user.hasPhoto as hasPhoto,
            user.birthday as birthday,
            {select_param + "," if select_param else ""}
            user.access_level as access_level
        FROM user
    """


async def get_user_by_id(telegram_id: int) -> User:
    sql = f"""
        {_get_user_base_sql()}
        WHERE user.telegram_id = {telegram_id}
    """
    user = await _get_user_from_db(sql)
    return user


async def _get_user_from_db(sql: str) -> User | None:
    user = await fetch_one(sql)
    if not user:
        return None
    if user["birthday"]:
        birthday = datetime.strptime(f"{user['birthday']}", rf"%Y-%m-%d")
    else:
        birthday = None
    return User(
            id=user["id"],
            name=user["name"],
            nickname=user["nickname"],
            city=user["city"],
            hasPhoto=user["hasPhoto"],
            birthday=birthday,
            access_level=get_access_level(user["access_level"]),
        )


### Updating and Inserting User's Data

async def update_user_parameter( user_id: int, param_name: str, param_value):
    match param_name:
        case 'hasPhoto':
            param_value = str(param_value).lower()
        case 'birthday':
            pass
        case 'access_level':
            param_value = str(param_value.value)
        case 'name'|'nickname'|'city':
            param_value = f"'{param_value}'"
        case _:
            raise ValueError(f"Invalid parameter name plased into update user function: {param_name}")
    sql = f"""
        UPDATE user
        SET {param_name} = {param_value}
        WHERE telegram_id = {user_id}
    """
    await execute(sql)


async def insert_user_id(telegram_id: int):
    sql_user = f"""INSERT INTO user VALUES ({telegram_id}, '', '', '', false, null, 1)"""
    sql_user_edit = f"""INSERT INTO user_edit VALUES ({telegram_id})"""
    await execute(sql_user)
    await execute(sql_user_edit)


async def delete_user(telegram_id: int):
    sql = f"""DELETE FROM user WHERE telegram_id = {telegram_id}"""
    await execute(sql)


async def delete_user_edit(telegram_id: int):
    sql = f"""DELETE FROM user_edit WHERE user_id = {telegram_id}"""
    await execute(sql)


async def update_statistic_parameter(user_id: int, event_id: int, param_name: str, param_value: int):
    sql = f"""
        UPDATE statistic
        SET {param_name} = {param_value}
        WHERE user_id = {user_id} AND event_id = {event_id}
    """
    await execute(sql)


async def insert_statistic_edit(editor_id: int, user_id: int, event_id: int):
    sql = f"""INSERT INTO statistic_edit VALUES ({editor_id}, {user_id}, {event_id})"""
    await execute(sql)


async def delete_statistic_edit(editor_id: int):
    sql = f"""DELETE FROM statistic_edit WHERE editor_id = {editor_id}"""
    await execute(sql)


async def get_statistic_edit(editor_id: int) -> dict[str, int]:
    sql = f"""SELECT * FROM statistic_edit WHERE editor_id = {editor_id}"""
    response = await fetch_one(sql)
    return response
