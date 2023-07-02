import datetime

import telegram
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from mafia_bot import config
from mafia_bot.handlers.response import send_response
from mafia_bot.handlers.keyboards import (
    get_view_user_profile_keyboard,
    get_userlist_keyboard,
    get_user_profile_keyboard,
    get_edit_user_profile_keyboard
)
from mafia_bot.templates import render_template
from mafia_bot.services.user import (
    get_user_by_id,
    get_userlist_by_event_id,
    update_user_parameter,
    delete_user
)


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user = await get_user_by_id(user_id)
    if not update.message:
        return
    await send_response(
        update,
        context,
        render_template(
            "user.j2",
            {"user": user}
        ),
        get_user_profile_keyboard(
            callback_prefix=f"{config.EDIT_USER_PROFILE_CALLBACK_PATTERN}{user_id}"
        )
    )

async def user_profile_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = _get_user_id(query.data)
    user = await get_user_by_id(user_id)
    await query.edit_message_text(
        text=render_template(
            "user.j2",
            {"user": user}
        ),
        reply_markup=get_user_profile_keyboard(
            callback_prefix=f"{config.EDIT_USER_PROFILE_CALLBACK_PATTERN}{user_id}"
        ),
        parse_mode=telegram.constants.ParseMode.HTML,
    )


async def view_user_profile_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    prev_callback = _get_prev_callback(query.data, config.VIEW_USER_PROFILE_CALLBACK_PATTERN)
    user_id = _get_user_id(query.data)
    user = await get_user_by_id(user_id)
    await query.edit_message_text(
        text=render_template(
            "user.j2",
            {"user": user}
        ),
        reply_markup=get_view_user_profile_keyboard(
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
                "user_profile": f"{config.VIEW_USER_PROFILE_CALLBACK_PATTERN}{query.data}_",
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


async def edit_user_profile_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    user_id = _get_user_id(query.data)
    await query.edit_message_text(
        text=render_template(
            "edit_profile_menu.j2"
        ),
        reply_markup=get_edit_user_profile_keyboard(
            {
                "name": f"{config.EDIT_USER_PROFILE_CALLBACK_PATTERN[:-1]}.name_{user_id}",
                "nickname": f"{config.EDIT_USER_PROFILE_CALLBACK_PATTERN[:-1]}.nickname_{user_id}",
                "city": f"{config.EDIT_USER_PROFILE_CALLBACK_PATTERN[:-1]}.city_{user_id}",
                "photo": f"{config.EDIT_USER_PROFILE_CALLBACK_PATTERN[:-1]}.photo_{user_id}",
                "back": f"{config.OWN_USER_PROFILE_CALLBACK_PATTERN}{user_id}"
            }
        ),
        parse_mode=telegram.constants.ParseMode.HTML,
    )


async def edit_user_parameter_start_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    param_name = _get_param_name(query.data)
    template = "edit_parameter_base.j2"
    if param_name == "photo":
        template = "edit_parameter_photo.j2"
    await query.edit_message_text(
        text=render_template(
            template
        ),
        parse_mode=telegram.constants.ParseMode.HTML,
    )
    return param_name


def _get_param_name(query_data: str) -> str:
    pattern_prefix_length = len(config.EDIT_USER_PROFILE_CALLBACK_PATTERN)
    pattern_postfix_length = query_data.rfind("_")
    param_name = query_data[pattern_prefix_length:pattern_postfix_length]
    return param_name


async def edit_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    param_value = update.message.text
    await update_user_parameter("name", param_value, user_id)
    await send_response(
        update,
        context,
        render_template("done.j2")
    )
    return ConversationHandler.END


async def edit_user_nickname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    param_value = update.message.text
    await update_user_parameter("nickname", param_value, user_id)
    await send_response(
        update,
        context,
        render_template("done.j2")
    )
    return ConversationHandler.END


async def edit_user_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    param_value = update.message.text
    await update_user_parameter("city", param_value, user_id)
    await send_response(
        update,
        context,
        render_template("done.j2")
    )
    return ConversationHandler.END


async def edit_user_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    param_value = update.message.text
    await send_response(
        update,
        context,
        render_template("done.j2")
    )
    return ConversationHandler.END


async def _cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await send_response(
        update,
        context,
        render_template("cancel.j2")
    )
    return ConversationHandler.END


def get_edit_user_conversation() -> ConversationHandler:
    pattern = rf"^{config.EDIT_USER_PROFILE_CALLBACK_PATTERN[:-1]}\.(.+)$"
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_user_parameter_start_button, pattern=pattern)],
        states={
            "name": [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_user_name)],
            "nickname": [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_user_nickname)],
            "city": [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_user_city)],
            "photo": [MessageHandler(filters.PHOTO, edit_user_photo)]
        },
        fallbacks=[MessageHandler(filters.COMMAND, _cancel)]
    )

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    await delete_user(user.id)
