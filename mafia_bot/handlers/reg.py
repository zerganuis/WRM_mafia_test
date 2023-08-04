from collections.abc import Iterable
import enum

import telegram
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from mafia_bot import config
from mafia_bot.handlers.response import send_text_response
from mafia_bot.handlers.profile import format_birthday_to_db
from mafia_bot.templates import render_template
from mafia_bot.services.user import (
    User,
    insert_user_id,
    delete_user,
    delete_user_edit,
    update_user_parameter,
    validate_user,
    AccessLevel
)

template_prefix = config.REG_TEMPLATES_DIR


class RegistrationState(enum.Enum):
    NAME: 'RegistrationState' = 0
    NICKNAME: 'RegistrationState' = 1
    BIRTHDAY: 'RegistrationState' = 2
    CITY: 'RegistrationState' = 3
    PHOTO: 'RegistrationState' = 4


@validate_user(AccessLevel.WALKER)
async def cmd_reg(update: Update, context: ContextTypes.DEFAULT_TYPE, access_level: AccessLevel) -> RegistrationState:
    if not update.message:
        return
    if access_level.value > 0:
        await send_text_response(
            update,
            context,
            "Вы уже зарегистрированы"
        )
        return ConversationHandler.END
    user_id = update.effective_user.id
    await insert_user_id(user_id)
    await send_text_response(
        update,
        context,
        render_template(
            f"{template_prefix}get_name.j2"
        )
    )
    return RegistrationState.NAME


async def _get_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> RegistrationState:
    user_id = update.message.from_user.id
    text = update.message.text
    await update_user_parameter(user_id, "name", text)
    await send_text_response(
        update,
        context,
        render_template(f"{template_prefix}get_nickname.j2")
    )
    return RegistrationState.NICKNAME


async def _get_user_nickname(update: Update, context: ContextTypes.DEFAULT_TYPE) -> RegistrationState:
    user_id = update.message.from_user.id
    text = update.message.text
    await update_user_parameter(user_id, "nickname", text)
    await send_text_response(
        update,
        context,
        render_template(f"{template_prefix}get_birthday.j2")
    )
    return RegistrationState.BIRTHDAY


async def _get_user_birthday(update: Update, context: ContextTypes.DEFAULT_TYPE) -> RegistrationState:
    user_id = update.message.from_user.id
    param_value = update.message.text
    try:
        param_value = format_birthday_to_db(param_value)
    except Exception:
        await send_text_response(
            update,
            context,
            "Вы неверно ввели дату, попробуйте еще раз:"
        )
        return RegistrationState.BIRTHDAY
    await update_user_parameter(user_id, "birthday", param_value)
    await send_text_response(
        update,
        context,
        render_template(f"{template_prefix}get_birthday_get_city.j2")
    )
    return RegistrationState.CITY


async def _skip_user_birthday(update: Update, context: ContextTypes.DEFAULT_TYPE) -> RegistrationState:
    await send_text_response(
        update,
        context,
        render_template(f"{template_prefix}skip_birthday_get_city.j2")
    )
    return RegistrationState.CITY


async def _get_user_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> RegistrationState:
    user_id = update.message.from_user.id
    text = update.message.text
    await update_user_parameter(user_id, "city", text)
    await send_text_response(
        update,
        context,
        render_template(f"{template_prefix}get_city_get_photo.j2")
    )
    return RegistrationState.PHOTO


async def _skip_user_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> RegistrationState:
    await send_text_response(
        update,
        context,
        render_template(f"{template_prefix}skip_city_get_photo.j2")
    )
    return RegistrationState.PHOTO


async def _get_user_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> RegistrationState:
    photo_file = await update.message.photo[-1].get_file()
    user_id = update.message.from_user.id
    path = config.USERS_PHOTOS_DIR.joinpath(f"{user_id}")
    await photo_file.download_to_drive(custom_path=path)
    await update_user_parameter(user_id, "hasPhoto", True)
    await delete_user_edit(user_id)
    await send_text_response(
        update,
        context,
        render_template(f"{template_prefix}get_photo.j2")
    )
    return ConversationHandler.END


async def _skip_user_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> RegistrationState:
    user_id = update.message.from_user.id
    await delete_user_edit(user_id)
    await send_text_response(
        update,
        context,
        render_template(f"{template_prefix}skip_photo.j2")
    )
    return ConversationHandler.END


async def _cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    await delete_user(user.id)
    await delete_user_edit(user.id)
    await send_text_response(
        update,
        context,
        render_template("cancel.j2")
    )
    return ConversationHandler.END


def get_registration_conversation() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("reg", cmd_reg)],
        states={
            RegistrationState.NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, _get_user_name)
            ],
            RegistrationState.NICKNAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, _get_user_nickname)
            ],
            RegistrationState.BIRTHDAY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, _get_user_birthday),
                CommandHandler("skip", _skip_user_birthday)
            ],
            RegistrationState.CITY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, _get_user_city),
                CommandHandler("skip", _skip_user_city)
            ],
            RegistrationState.PHOTO: [
                MessageHandler(filters.PHOTO, _get_user_photo),
                CommandHandler("skip", _skip_user_photo)
            ],
        },
        fallbacks=[MessageHandler(filters.COMMAND & ~filters.Regex("^/skip$"), _cancel)],
    )
