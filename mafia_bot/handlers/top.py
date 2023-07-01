import datetime

import telegram
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from mafia_bot import config
from mafia_bot.handlers.response import send_response
from mafia_bot.handlers.keyboards import get_top_keyboard
from mafia_bot.templates import render_template
from mafia_bot.services.user import get_userlist, get_top_users

ALLTIME_TOP = 0
MONTH_TOP = 1


async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _top_alltime(update, context)
    await _top_month(update, context)


async def top_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    period = _get_period(query.data)
    users = list(await get_top_users(period))
    await query.edit_message_text(
        text=render_template(
            "top.j2",
            {"period": "За последние 30 дней" if period == datetime.timedelta(days=30) else "За все время", "userlist": users}
        ),
        reply_markup=get_top_keyboard(
            users,
            f"{config.USER_PROFILE_CALLBACK_PATTERN}{query.data}_",
            lambda user: f"{user.name} ({user.total_score})"
        ),
        parse_mode=telegram.constants.ParseMode.HTML,
    )


def _get_period(query_data) -> tuple[int, datetime.timedelta]:
    pattern_prefix_length = len(config.TOP_CALLBACK_PATTERN)
    top_type = int(query_data[pattern_prefix_length:])
    period = datetime.timedelta(days=0)
    if top_type:
        period = datetime.timedelta(days=30)
    return period


async def _top_alltime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    period = datetime.timedelta(days=0)
    users = list(await get_top_users(period))
    if not update.message:
        return
    await send_response(
        update,
        context,
        render_template(
            "top.j2",
            {"period": "За все время", "userlist": users}
        ),
        get_top_keyboard(
            users,
            f"{config.USER_PROFILE_CALLBACK_PATTERN}{config.TOP_CALLBACK_PATTERN}{ALLTIME_TOP}_",
            lambda user: f"{user.name} ({user.total_score})"
        )
    )


async def _top_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    period = datetime.timedelta(days=30)
    users = list(await get_top_users(period))
    if not update.message:
        return
    await send_response(
        update,
        context,
        render_template(
            "top.j2",
            {"period": "За последние 30 дней", "userlist": users}
        ),
        get_top_keyboard(
            users,
            f"{config.USER_PROFILE_CALLBACK_PATTERN}{config.TOP_CALLBACK_PATTERN}{MONTH_TOP}_",
            lambda user: f"{user.name} ({user.total_score})"
        )
    )
