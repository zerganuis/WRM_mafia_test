import datetime

import telegram
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from mafia_bot import config
from mafia_bot.handlers.response import send_response
from mafia_bot.handlers.keyboards import get_user_profile_keyboard
from mafia_bot.templates import render_template

from mafia_bot.services.user import get_user_by_id, User

async def user_profile_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    prev_callback = _get_prev_callback(query.data)
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

def _get_prev_callback(query_data) -> str:
    pattern_prefix_length = len(config.USER_PROFILE_CALLBACK_PATTERN)
    pattern_postfix_length = query_data.rfind("_")
    return query_data[pattern_prefix_length:pattern_postfix_length]