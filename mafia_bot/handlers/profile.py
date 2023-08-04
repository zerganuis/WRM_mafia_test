from copy import copy
from datetime import timedelta, date

import telegram
from telegram import Update, InputMediaPhoto
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from mafia_bot import config
from mafia_bot.templates import render_template

from mafia_bot.services.access import AccessLevel
from mafia_bot.services.user import (
    validate_user,
    get_user_statistic,
    get_user_by_id,
    update_user_parameter,
    delete_user
)

from mafia_bot.handlers.response import send_text_response, send_photos_response
from mafia_bot.handlers.menu import get_id, get_prev_callback
from mafia_bot.handlers.keyboards import (
    get_user_profile_keyboard,
    get_edit_user_profile_keyboard,
)


### Profile Command

@validate_user(AccessLevel.USER)
async def cmd_profile(update: Update, context: ContextTypes.DEFAULT_TYPE, access_level):
    if not update.message:
        return
    user_id = update.message.from_user.id
    user = await get_user_by_id(user_id)
    user_stat_period_1 = await get_user_statistic(user_id, timedelta(days=30))
    user_stat_period_2 = await get_user_statistic(user_id, timedelta(days=90))
    if user.hasPhoto:
        path_to_photo = config.USERS_PHOTOS_DIR / str(user_id)
    else:
        path_to_photo = config.BASE_USER_PHOTO

    callback_prefix = {
        "edit_profile": f"{config.EDIT_USER_PROFILE_CALLBACK_PATTERN}{user_id}"
    }
    
    await send_photos_response(
        update,
        context,
        render_template(
            "profile.j2",
            {
                "user": user,
                "stat_periods": [user_stat_period_1, user_stat_period_2]
            }
        ),
        get_user_profile_keyboard(
            callback_prefix=callback_prefix,
            user_access_level_id=user.access_level.value
        ),
        path_to_photo
    )


@validate_user(AccessLevel.USER)
async def user_profile_button(update: Update, context: ContextTypes.DEFAULT_TYPE, access_level: AccessLevel):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    user_id = get_id(query.data)
    user = await get_user_by_id(user_id)
    user_stat_period_1 = await get_user_statistic(user_id, timedelta(days=30))
    user_stat_period_2 = await get_user_statistic(user_id, timedelta(days=90))
    prev_callback = get_prev_callback(query.data)
    callback_prefix = {}
    if not prev_callback:
        callback_prefix["edit_profile"] = f"{config.EDIT_USER_PROFILE_CALLBACK_PATTERN}{user_id}"
    else:
        callback_prefix["back"] = prev_callback
        if access_level == AccessLevel.ADMIN:
            if config.EVENT_PARTICIPANTS_CALLBACK_PATTERN in prev_callback:
                callback_prefix["grade"] = f"{config.GRADE_CALLBACK_PATTERN}{query.data}_0"
            elif user_id != update.effective_user.id:
                callback_prefix["change_access"] = f"{config.CHANGE_ACCESS_CALLBACK_PATTERN}{prev_callback}_{user_id}"
    if user.hasPhoto:
        path_to_photo = config.USERS_PHOTOS_DIR / str(user_id)
    else:
        path_to_photo = config.BASE_USER_PHOTO
    await query.edit_message_media(
        InputMediaPhoto(
            media=open(path_to_photo, 'rb'),
            caption=render_template(
                "profile.j2",
                {
                    "user": user,
                    "stat_periods": [user_stat_period_1, user_stat_period_2]
                }
            ),
            parse_mode=telegram.constants.ParseMode.HTML,
        ),
        reply_markup=get_user_profile_keyboard(
            callback_prefix=callback_prefix,
            user_access_level_id=user.access_level.value
        )
    )


@validate_user(AccessLevel.USER)
async def change_access_button(update: Update, context: ContextTypes.DEFAULT_TYPE, access_level: AccessLevel):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    prev_callback = get_prev_callback(query.data)
    user_id = get_id(query.data)
    user = await get_user_by_id(user_id)
    callback_prefix = {}
    if not prev_callback:
        callback_prefix["edit_profile"] = f"{config.EDIT_USER_PROFILE_CALLBACK_PATTERN}{user_id}"
    else:
        callback_prefix["back"] = prev_callback
        if access_level == AccessLevel.ADMIN:
            if config.EVENT_PARTICIPANTS_CALLBACK_PATTERN in prev_callback:
                callback_prefix["grade"] = f"{config.GRADE_CALLBACK_PATTERN}{query.data}_0"
            elif user_id != update.effective_user.id:
                callback_prefix["change_access"] = f"{config.CHANGE_ACCESS_CALLBACK_PATTERN}{prev_callback}_{user_id}"
    if user.access_level == AccessLevel.USER:
        user_access_level = AccessLevel.ADMIN
    else:
        user_access_level = AccessLevel.USER
    await update_user_parameter(user_id, 'access_level', user_access_level)
    await update.effective_message.edit_reply_markup(
        reply_markup=get_user_profile_keyboard(
            callback_prefix=callback_prefix,
            user_access_level_id=user_access_level.value
        )
    )


### Edit User Profile

async def edit_user_profile_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    user_id = get_id(query.data)
    edit_parameters = {
        'name': 'Имя',
        'nickname': 'Игровое имя',
        'city': 'Город',
        'photo': 'Фото',
        'birthday': "Дата рождения"
    }
    prev_callback = get_prev_callback(query.data)
    if not prev_callback:
        prev_callback = f"{config.USER_PROFILE_CALLBACK_PATTERN}{user_id}"
    await query.edit_message_caption(
        caption=render_template(
            "edit_profile_menu.j2"
        ),
        reply_markup=get_edit_user_profile_keyboard(
            edit_parameters,
            user_id,
            {
                "prefix": config.EDIT_USER_PARAMETER_CALLBACK_PATTERN,
                "back": prev_callback
            }
        ),
        parse_mode=telegram.constants.ParseMode.HTML,
    )


async def edit_user_parameter_start_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    param_name = get_prev_callback(query.data)
    template = "edit_parameter_base.j2"
    if param_name == "photo":
        template = "edit_parameter_photo.j2"
    elif param_name == "birthday":
        template = "edit_parameter_birthday.j2"
    await query.edit_message_caption(
        caption=render_template(template),
        parse_mode=telegram.constants.ParseMode.HTML,
    )
    return param_name


def format_birthday_to_db(text: str) -> str:
    day, month = text.split('.')
    to_date = date(year=1, month=int(month), day=int(day))
    return f"date('{to_date}')"


async def edit_user_parameter(update: Update, context: ContextTypes.DEFAULT_TYPE, param_name: str):
    user_id = update.message.from_user.id
    if param_name == 'photo':
        photo_file = await update.message.photo[-1].get_file()
        path = config.USERS_PHOTOS_DIR.joinpath(f"{user_id}")
        await photo_file.download_to_drive(custom_path=path)
        await update_user_parameter(user_id, "hasPhoto", True)
    elif param_name == 'birthday':
        param_value = update.message.text
        try:
            param_value = format_birthday_to_db(param_value)
        except Exception:
            await send_text_response(
                update,
                context,
                "Вы неверно ввели дату, попробуйте еще раз:"
            )
            return "birthday"
        await update_user_parameter(user_id, param_name, param_value)
    else:
        param_value = update.message.text
        await update_user_parameter(user_id, param_name, param_value)
    await send_text_response(
        update,
        context,
        render_template("done.j2")
    )
    return ConversationHandler.END


async def _edit_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await edit_user_parameter(update, context, "name")


async def _edit_user_nickname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await edit_user_parameter(update, context, "nickname")


async def _edit_user_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await edit_user_parameter(update, context, "city")


async def _edit_user_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await edit_user_parameter(update, context, "photo")


async def _edit_user_birthday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await edit_user_parameter(update, context, "birthday")


async def _cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await send_text_response(
        update,
        context,
        render_template("cancel.j2")
    )
    return ConversationHandler.END


def get_edit_user_conversation() -> ConversationHandler:
    pattern = rf"^{config.EDIT_USER_PARAMETER_CALLBACK_PATTERN}(.+)$"
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_user_parameter_start_button, pattern=pattern)],
        states={
            "name": [MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                _edit_user_name
                )],
            "nickname": [MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                _edit_user_nickname
                )],
            "city": [MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                _edit_user_city
                )],
            "birthday": [MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                _edit_user_birthday
                )],
            "photo": [MessageHandler(
                filters.PHOTO,
                _edit_user_photo
                )]
        },
        fallbacks=[MessageHandler(filters.COMMAND, _cancel)]
    )


### Delete User From DB

async def cmd_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    await delete_user(user_id)
