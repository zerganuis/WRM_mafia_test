from collections.abc import Iterable
from datetime import timedelta

from mafia_bot import config
from mafia_bot.db import fetch_all
from mafia_bot.services.user import User
from mafia_bot.services.lists import group_by_pages


async def get_userlist(
        period: timedelta | None = None,
        limit: int | None = None
) -> Iterable[Iterable[User]]:
    select_param = """IIF(total_table.total_score is null, 0.0, total_table.total_score) as total_score"""
    sql = f"""
        {_userlist_base_sql(select_param)}
        LEFT JOIN (
            SELECT
                total(statistic.score) as total_score,
                statistic.user_id as user_id
            FROM statistic
            LEFT JOIN event ON event.id = statistic.event_id
            WHERE
                event.datetime < datetime('now')
            AND
                event.datetime > {
                    f"datetime('now', '-{period.total_seconds()} seconds')"
                        if period else "0"
                }
            GROUP BY statistic.user_id
        ) total_table ON total_table.user_id = user.telegram_id
        ORDER BY total_score DESC
        {f"LIMIT {limit}" if limit else ""}
    """
    userlist = await _get_userlist_from_db(sql)
    return group_by_pages(userlist, config.USERLIST_PAGE_LENGTH)


async def _get_userlist_from_db(sql: str) -> Iterable[User]:
    userlist_raw = await fetch_all(sql)
    return [
        User(
            id=user["id"],
            name=user["name"],
            nickname=user["nickname"],
            total_score=user["total_score"]
        )
        for user in userlist_raw
    ]


def _userlist_base_sql(select_param: str | None = None) -> str:
    return f"""
        SELECT
            {select_param + "," if select_param else ""}
            user.telegram_id as id,
            user.name as name,
            user.nickname as nickname
        FROM user"""


async def get_event_participants(event_id: int) -> Iterable[User]:
    base_sql = _userlist_base_sql()
    cut = base_sql.find("FROM")
    sql = f"""
        {base_sql[:cut]}
        FROM statistic
        LEFT JOIN user ON user.telegram_id = statistic.user_id
        WHERE statistic.event_id = {event_id}"""
    userlist = await _get_userlist_from_db(sql)
    return userlist
