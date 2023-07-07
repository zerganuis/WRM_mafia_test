from pathlib import Path
from typing import cast

import telegram
from telegram import Chat, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from mafia_bot import config


async def send_response(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    response: str,
    keyboard: InlineKeyboardMarkup | None = None,
) -> None:
    args = {
        "chat_id": _get_chat_id(update),
        "disable_web_page_preview": True,
        "text": response,
        "parse_mode": telegram.constants.ParseMode.HTML,
    }
    if keyboard:
        args["reply_markup"] = keyboard

    await context.bot.send_message(**args)


async def send_response_photo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    response: str,
    keyboard: InlineKeyboardMarkup | None = None,
    path_to_photo: Path = config.BASE_PHOTO
) -> None:
    args = {
        "chat_id": _get_chat_id(update),
        "caption": response,
        "parse_mode": telegram.constants.ParseMode.HTML,
    }
    if keyboard:
        args["reply_markup"] = keyboard
    with open(path_to_photo, 'rb') as photo:    
        args["photo"] = photo
        await context.bot.send_photo(**args)


def _get_chat_id(update: Update) -> int:
    return cast(Chat, update.effective_chat).id
