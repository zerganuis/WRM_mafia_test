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
from mafia_bot.services.user import User

template_prefix = "reg/"

class RegistrationState(enum.Enum):
    NAME: 'RegistrationState' = 0
    NICKNAME: 'RegistrationState' = 1
    CITY: 'RegistrationState' = 2
    PHOTO: 'RegistrationState' = 3


async def registration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> RegistrationState:
    if not update.message:
        return
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
    user = update.message.from_user
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
    await update.message.reply_text(
        "Регистрация отменена")
    return ConversationHandler.END


def get_registration_conversation(entry_point: CommandHandler) -> ConversationHandler:
    return ConversationHandler(
        entry_points=[entry_point],
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
        fallbacks=[CommandHandler("cancel", _cancel)],
    )
