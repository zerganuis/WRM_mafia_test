from pathlib import Path
from typing import cast

import telegram
from telegram import Chat, InlineKeyboardMarkup, Update, InputMediaPhoto
from telegram.ext import ContextTypes
from mafia_bot import config


async def send_text_response(
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


async def send_photos_response(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    caption: str,
    keyboard: InlineKeyboardMarkup | None = None,
    path_to_photos: Path = config.PHOTOS_DIR
) -> None:
    args = {
        "chat_id": _get_chat_id(update),
        "caption": caption,
        "parse_mode": telegram.constants.ParseMode.HTML,
    }
    if keyboard:
        args["reply_markup"] = keyboard
    if path_to_photos.is_dir():
        files_in_dir = [filepath for filepath in path_to_photos.iterdir()]
        if len(files_in_dir) > 0:
            args["media"] = [
                InputMediaPhoto(media=open(picture, 'rb'), filename="photo")
                for picture in files_in_dir if picture.is_file()
            ]
    else:
        args["media"] = [
            InputMediaPhoto(media=open(path_to_photos, 'rb'), filename="photo")
        ]
    
    if args.get("media", None):
        if len(args["media"]) > 1:
            args.pop("reply_markup")
            await context.bot.send_media_group(**args)
        else:
            args["photo"] = args.pop("media")[0].media
            await context.bot.send_photo(**args)
    else:
        await send_text_response(update, context, caption)


def _get_chat_id(update: Update) -> int:
    return cast(Chat, update.effective_chat).id
