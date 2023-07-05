import datetime

import telegram
from telegram import Update
from telegram.ext import ContextTypes

from mafia_bot import config
from mafia_bot.handlers.response import send_response
from mafia_bot.handlers.keyboards import get_top_menu_keyboard, get_userlist_keyboard
from mafia_bot.templates import render_template
from mafia_bot.services.user import get_top_users, validate_user, AccessLevel


_all_periods = {
    "ALLTIME": "За все время",
    "MONTH": "За последний месяц"
}

@validate_user(AccessLevel.USER)
async def top(update: Update, context: ContextTypes.DEFAULT_TYPE, access_level):
    if not update.message:
        return
    await send_response(
        update,
        context,
        render_template(
            "top_menu.j2"
        ),
        get_top_menu_keyboard(
            _all_periods,
            f"{config.TOP_SUBMENU_CALLBACK_PATTERN}"
        )
    )


async def top_menu_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    await query.edit_message_text(
        text=render_template(
            "top_menu.j2"
        ),
        reply_markup=get_top_menu_keyboard(
            _all_periods,
            f"{config.TOP_SUBMENU_CALLBACK_PATTERN}"
        ),
        parse_mode=telegram.constants.ParseMode.HTML,
    )


async def top_submenu_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    period = _get_period(query.data)
    timedelta = _get_timedelta(period)
    users = list(await get_top_users(timedelta))
    await query.edit_message_text(
        text=render_template(
            "top_submenu.j2",
            {"period": _all_periods[period].lower()}
        ),
        reply_markup=get_userlist_keyboard(
            users,
            {
                "user_profile": f"{config.VIEW_USER_PROFILE_CALLBACK_PATTERN}{query.data}_",
                "back": f"{config.TOP_MENU_CALLBACK_PATTERN}0"
            },
            lambda user: f"{user.name} ({user.total_score})"
        ),
        parse_mode=telegram.constants.ParseMode.HTML,
    )

def _get_period(query_data) -> str:
    pattern_prefix_length = len(config.TOP_SUBMENU_CALLBACK_PATTERN)
    period = query_data[pattern_prefix_length:]
    return period

def _get_timedelta(period):
    match period:
        case "ALLTIME":
            return datetime.timedelta(days=0)
        case "MONTH":
            return datetime.timedelta(days=30)
        case _:
            raise ValueError(f"Неопознанный период: {period}")