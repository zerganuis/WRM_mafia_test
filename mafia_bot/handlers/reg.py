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
from mafia_bot.handlers.response import send_response
from mafia_bot.templates import render_template
from mafia_bot.services.event import Event
from mafia_bot.services.user import (
    User,
    insert_user_id,
    delete_user,
    delete_user_registration,
    update_user_parameter,
    validate_user,
    AccessLevel
)

template_prefix = "reg/"


class RegistrationState(enum.Enum):
    NAME: 'RegistrationState' = 0
    NICKNAME: 'RegistrationState' = 1
    CITY: 'RegistrationState' = 2
    PHOTO: 'RegistrationState' = 3


@validate_user(AccessLevel.WALKER)
async def registration(update: Update, context: ContextTypes.DEFAULT_TYPE, access_level: AccessLevel) -> RegistrationState:
    if access_level.value > 0:
        await send_response(
            update,
            context,
            "Вы уже зарегистрированы"
        )
        return ConversationHandler.END
    user = update.effective_user
    if not update.message:
        return
    await insert_user_id(user.id)
    await send_response(
        update,
        context,
        render_template(
            f"{template_prefix}reg_start.j2"
        )
    )
    return RegistrationState.NAME


async def _get_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> RegistrationState:
    user = update.message.from_user
    text = update.message.text
    await update_user_parameter(
        "name",
        text,
        user.id
    )
    await send_response(
        update,
        context,
        render_template(
            f"{template_prefix}get_user_name.j2"
        )
    )
    return RegistrationState.NICKNAME


async def _get_user_nickname(update: Update, context: ContextTypes.DEFAULT_TYPE) -> RegistrationState:
    user = update.message.from_user
    text = update.message.text
    await update_user_parameter(
        "nickname",
        text,
        user.id
    )
    await send_response(
        update,
        context,
        render_template(
            f"{template_prefix}get_user_nickname.j2"
        )
    )
    return RegistrationState.CITY


async def _get_user_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> RegistrationState:
    user = update.message.from_user
    text = update.message.text
    await update_user_parameter(
        "city",
        text,
        user.id
    )
    await send_response(
        update,
        context,
        render_template(
            f"{template_prefix}get_user_city.j2"
        )
    )
    return RegistrationState.PHOTO


async def _skip_user_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> RegistrationState:
    user = update.message.from_user
    await send_response(
        update,
        context,
        render_template(
            f"{template_prefix}skip_user_city.j2"
        )
    )
    return RegistrationState.PHOTO


async def _get_user_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> RegistrationState:
    photo_file = await update.message.photo[-1].get_file()
    user = update.message.from_user
    path = config.PHOTOS_DIR.joinpath(f"{user.id}")
    await photo_file.download_to_drive(custom_path=path)
    await update_user_parameter(
        "hasPhoto",
        'true',
        user.id
    )
    await delete_user_registration(user.id)
    await send_response(
        update,
        context,
        render_template(
            f"{template_prefix}get_user_photo.j2"
        )
    )
    return ConversationHandler.END


async def _skip_user_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> RegistrationState:
    user = update.message.from_user
    await delete_user_registration(user.id)
    await send_response(
        update,
        context,
        render_template(
            f"{template_prefix}skip_user_photo.j2"
        )
    )
    return ConversationHandler.END


async def _cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    await delete_user(user.id)
    await delete_user_registration(user.id)
    await send_response(
        update,
        context,
        render_template("cancel.j2")
    )
    return ConversationHandler.END


def get_registration_conversation() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("reg", registration)],
        states={
            RegistrationState.NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, _get_user_name)
            ],
            RegistrationState.NICKNAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, _get_user_nickname)
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
