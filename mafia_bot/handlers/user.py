import datetime

import telegram
from telegram import Update, InputMediaPhoto, PhotoSize
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
    get_edit_user_profile_keyboard,
    get_grade_user_keyboard
)
from mafia_bot.templates import render_template
from mafia_bot.services.user import (
    get_user_by_id,
    get_userlist_by_event_id,
    update_user_parameter,
    delete_user,
    edit_statistic_score,
    edit_statistic_is_winner,
    insert_edit_statistic,
    get_edit_statistic,
    delete_edit_statistic,
    validate_user,
    AccessLevel,
    update_user_access_level
)


@validate_user(AccessLevel.USER)
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE, access_level):
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
    if not query.data or not query.data.strip():
        return
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

@validate_user(AccessLevel.USER)
async def view_user_profile_button(update: Update, context: ContextTypes.DEFAULT_TYPE, access_level: AccessLevel):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    prev_callback = _get_prev_callback(query.data, config.VIEW_USER_PROFILE_CALLBACK_PATTERN)
    user_id = _get_user_id(query.data)
    user = await get_user_by_id(user_id)
    callback_prefix = {
        # "grade": f"{config.GRADE_CALLBACK_PATTERN}{query.data}_0",
        "back": prev_callback
    }
    if access_level == AccessLevel.ADMIN:
        callback_prefix["grade"] = f"{config.GRADE_CALLBACK_PATTERN}{query.data}_0"
        callback_prefix["access_admin"] = f"{config.CHANGE_ACCESS_CALLBACK_PATTERN}{user_id}_2"
        callback_prefix["access_user"] = f"{config.CHANGE_ACCESS_CALLBACK_PATTERN}{user_id}_1"
    await query.edit_message_text(
        text=render_template(
            "user.j2",
            {"user": user}
        ),
        reply_markup=get_view_user_profile_keyboard(callback_prefix=callback_prefix),
        parse_mode=telegram.constants.ParseMode.HTML,
    )


async def change_access_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    access_level = _get_user_id(query.data)
    user_id = _get_user_id(query.data[:-2])
    await update_user_access_level(access_level, user_id)


async def grade_user_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    user_id = _get_user_id(query.data[:-2])
    event_id = _get_event_id(query.data[:-len(f"_{user_id}_0")])
    user = await get_user_by_id(user_id)
    prev_callback = "".join((
        config.VIEW_USER_PROFILE_CALLBACK_PATTERN,
        config.USERLIST_CALLBACK_PATTERN,
        config.EVENT_PROFILE_CALLBACK_PATTERN,
        f"{event_id}_",
        f"{user_id}"
    ))
    await query.edit_message_text(
        text=render_template(
            "grade_user.j2",
            {"user": user}
        ),
        reply_markup=get_grade_user_keyboard(
            callback_prefix={
                "grade": f"{config.GRADE_REQEST_CALLBACK_PATTERN}{event_id}_{user_id}",
                "winner": f"{config.ISWINNER_CALLBACK_PATTERN}{event_id}_{user_id}_1",
                "loser": f"{config.ISWINNER_CALLBACK_PATTERN}{event_id}_{user_id}_0",
                "back": prev_callback
            }
        ),
        parse_mode=telegram.constants.ParseMode.HTML,
    )


async def is_winner_user_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    isWinner = bool(_get_user_id(query.data))
    user_id = _get_user_id(query.data[:-2])
    event_id = _get_event_id(query.data[:-len(f"_{user_id}_0")])
    await edit_statistic_is_winner(user_id, event_id, isWinner)


def _get_user_id(query_data: str) -> int:
    pattern_prefix_length = query_data.rfind("_") + 1
    user_id = int(query_data[pattern_prefix_length:])
    return user_id

def _get_event_id(query_data: str) -> int:
    pattern_prefix_length = query_data.rfind("_") + 1
    event_id = int(query_data[pattern_prefix_length:])
    return event_id

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


async def _edit_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    param_value = update.message.text
    await update_user_parameter("name", param_value, user_id)
    await send_response(
        update,
        context,
        render_template("done.j2")
    )
    return ConversationHandler.END


async def _edit_user_nickname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    param_value = update.message.text
    await update_user_parameter("nickname", param_value, user_id)
    await send_response(
        update,
        context,
        render_template("done.j2")
    )
    return ConversationHandler.END


async def _edit_user_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    param_value = update.message.text
    await update_user_parameter("city", param_value, user_id)
    await send_response(
        update,
        context,
        render_template("done.j2")
    )
    return ConversationHandler.END


async def _edit_user_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    user = update.message.from_user
    path = config.PHOTOS_DIR.joinpath(f"{user.id}.png")
    await photo_file.download_to_drive(custom_path=path)
    await update_user_parameter(
        "photo_link",
        path,
        user.id
    )
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
            "name": [MessageHandler(filters.TEXT & ~filters.COMMAND, _edit_user_name)],
            "nickname": [MessageHandler(filters.TEXT & ~filters.COMMAND, _edit_user_nickname)],
            "city": [MessageHandler(filters.TEXT & ~filters.COMMAND, _edit_user_city)],
            "photo": [MessageHandler(filters.PHOTO, _edit_user_photo)]
        },
        fallbacks=[MessageHandler(filters.COMMAND, _cancel)]
    )

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    await delete_user(user.id)


async def _edit_user_score_start_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    user_id = _get_user_id(query.data)
    event_id = _get_event_id(query.data[:-len(f"_{user_id}")])
    await insert_edit_statistic(user_id, event_id)
    await send_response(update, context, render_template("score_edit.j2"))
    return 1

async def _edit_user_score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ids = await get_edit_statistic()
    param_value = int(update.message.text.strip())
    await edit_statistic_score(ids['user_id'], ids['event_id'], param_value)
    await delete_edit_statistic()
    await send_response(update, context, render_template("done.j2"))
    return ConversationHandler.END

def get_edit_user_score_conversation() -> ConversationHandler:
    pattern = rf"^{config.GRADE_REQEST_CALLBACK_PATTERN}(.+)$"
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(_edit_user_score_start_button, pattern=pattern)],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, _edit_user_score)]
        },
        fallbacks=[MessageHandler(filters.COMMAND, _cancel)]
    )
