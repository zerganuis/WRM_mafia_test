import telegram
from telegram import Update
from telegram.ext import ContextTypes

from mafia_bot import config
from mafia_bot.handlers.keyboards import get_grade_user_keyboard
from mafia_bot.templates import render_template
from mafia_bot.handlers.menu import get_id, get_prev_callback, get_menu
from mafia_bot.services.user import get_user_by_id


async def grade_user_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return

    prev_callback = get_prev_callback(query.data)
    menu = get_menu(query.data)
    user_id = get_id(menu[1])
    event_id = get_id(menu[3])
    user = await get_user_by_id(user_id)

    await query.edit_message_caption(
        caption=render_template(
            "grade_user.j2",
            {"user": user}
        ),
        reply_markup=get_grade_user_keyboard(
            callback_prefix={
                "score": f"{config.GRADE_REQEST_CALLBACK_PATTERN}__{event_id}_{user_id}_score",
                "game_count": f"{config.GRADE_REQEST_CALLBACK_PATTERN}__{event_id}_{user_id}_gamecount",
                "win_count": f"{config.GRADE_REQEST_CALLBACK_PATTERN}__{event_id}_{user_id}_wincount",
                "back": prev_callback
            }
        ),
        parse_mode=telegram.constants.ParseMode.HTML,
    )
