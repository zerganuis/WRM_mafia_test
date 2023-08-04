import os

from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes

from mafia_bot import config
from mafia_bot.templates import render_template
from mafia_bot.handlers.menu import get_id, get_prev_callback
from mafia_bot.handlers.keyboards import get_photolist_keyboard, get_delete_photo_type_keyboard
from mafia_bot.handlers.response import send_photos_response, send_text_response
from mafia_bot.services.user import validate_user, AccessLevel

@validate_user(AccessLevel.ADMIN)
async def cmd_deletephoto(update: Update, context: ContextTypes.DEFAULT_TYPE, access_level: AccessLevel):
    if not update.message:
        return
    await send_photos_response(
        update,
        context,
        render_template("deletephoto.j2"),
        get_delete_photo_type_keyboard({
            "Мафия": f"{config.DELETE_PHOTO_CALLBACK_PATTERN}mafia_0",
            "Денежный поток": f"{config.DELETE_PHOTO_CALLBACK_PATTERN}flow_0",
            "Бункер": f"{config.DELETE_PHOTO_CALLBACK_PATTERN}bunker_0",
            "Команда /info": f"{config.DELETE_PHOTO_CALLBACK_PATTERN}info_0",
        })
    )


async def delete_photo_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    current_photo_index = get_id(query.data)
    event_type = get_prev_callback(query.data)
    photo_path = config.EVENT_PHOTOS_DIR / event_type
    if event_type == "info":
        photo_path = config.INFO_PHOTOS_DIR
    photolist = [photo for photo in photo_path.iterdir() if photo.is_file()]
    await query.edit_message_media(
        InputMediaPhoto(
            media=open(photolist[current_photo_index], "rb")
        ),
        reply_markup=get_photolist_keyboard(
            current_photo_index=current_photo_index,
            photo_count=len(photolist),
            callback_prefix={
                "page": f"{config.DELETE_PHOTO_CALLBACK_PATTERN}{event_type}_",
                "delete": f"{config.SUBMIT_DELETE_PHOTO_CALLBACK_PATTERN}{event_type}_{current_photo_index}"
            }
        )
    )


async def submit_delete_photo_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    current_photo_index = get_id(query.data)
    event_type = get_prev_callback(query.data)
    photo_path = config.EVENT_PHOTOS_DIR / event_type
    if event_type == "info":
        photo_path = config.INFO_PHOTOS_DIR
    photolist = [photo for photo in photo_path.iterdir() if photo.is_file()]
    os.remove(photolist[current_photo_index])
    await send_text_response(
        update,
        context,
        "Фото удалено"
    )
