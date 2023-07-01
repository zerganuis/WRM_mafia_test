import datetime

import telegram
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from mafia_bot import config
from mafia_bot.handlers.response import send_response
from mafia_bot.handlers.keyboards import get_user_profile_keyboard, get_userlist_keyboard
from mafia_bot.templates import render_template

from mafia_bot.services.user import get_user_by_id, User, get_userlist_by_event_id

async def user_profile_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    prev_callback = _get_prev_callback(query.data, config.USER_PROFILE_CALLBACK_PATTERN)
    user_id = _get_user_id(query.data)
    user = await get_user_by_id(user_id)
    await query.edit_message_text(
        text=render_template(
            "user.j2",
            {"user": user}
        ),
        reply_markup=get_user_profile_keyboard(
            callback_prefix=prev_callback
        ),
        parse_mode=telegram.constants.ParseMode.HTML,
    )

def _get_user_id(query_data: str) -> int:
    pattern_prefix_length = query_data.rfind("_") + 1
    user_id = int(query_data[pattern_prefix_length:])
    return user_id

def _get_prev_callback(query_data, current_callback) -> str:
    pattern_prefix_length = len(current_callback)
    pattern_postfix_length = query_data.rfind("_")
    return query_data[pattern_prefix_length:pattern_postfix_length]


async def userlist_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    prev_callback = _get_prev_callback(query.data, config.USERLIST_CALLBACK_PATTERN)
    event_id = _get_event_id(query.data)
    users = list(await get_userlist_by_event_id(event_id))
    await query.edit_message_text(
        text=render_template(
            "userlist.j2"
        ),
        reply_markup=get_userlist_keyboard(
            users,
            {
                "user_profile": f"{config.USER_PROFILE_CALLBACK_PATTERN}{query.data}_",
                "back": f"{prev_callback}_{event_id}"
            },
            lambda user: f"{user.nickname}"
        ),
        parse_mode=telegram.constants.ParseMode.HTML,
    )

def _get_event_id(query_data):
    pattern_prefix_length = query_data.rfind("_") + 1
    event_id = int(query_data[pattern_prefix_length:])
    return event_id
