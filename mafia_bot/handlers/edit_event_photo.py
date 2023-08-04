from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes

from mafia_bot import config
from mafia_bot.handlers.menu import get_id, get_prev_callback
from mafia_bot.services.event import get_event_by_id
from mafia_bot.handlers.keyboards import get_photolist_keyboard
from mafia_bot.services.event import get_edit_event_id
from mafia_bot.handlers.response import send_photos_response, send_text_response

async def reg_event_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    event_id = await get_edit_event_id(user_id)
    event = await get_event_by_id(event_id)
    event_type = event.event_type
    photo_path = config.EVENT_PHOTOS_DIR / event_type
    photolist = [photo for photo in photo_path.iterdir() if photo.is_file()]
    current_photo_index = 0
    if photolist:
        await send_photos_response(
            update,
            context,
            '',
            get_photolist_keyboard(
                current_photo_index=current_photo_index,
                photo_count=len(photolist),
                callback_prefix={
                    "page": f"{config.EVENT_PHOTOS_CALLBACK_PATTERN}{event_type}_",
                    "submit": f"{config.SUBMIT_PHOTO_CALLBACK_PATTERN}{current_photo_index}"
                }
            ),
            photolist[current_photo_index]
        )
    else:
        await send_text_response(
            update,
            context,
            "Список фотографий пуст"
        )


async def edit_event_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    query = update.callback_query
    event_id = get_id(query.data)
    event = await get_event_by_id(event_id)
    event_type = event.event_type
    photo_path = config.EVENT_PHOTOS_DIR / event_type
    photolist = [photo for photo in photo_path.iterdir() if photo.is_file()]
    current_photo_index = 0
    if photolist:
        await query.edit_message_media(
            InputMediaPhoto(
                media=open(photolist[current_photo_index], "rb")
            ),
            reply_markup=get_photolist_keyboard(
                current_photo_index=current_photo_index,
                photo_count=len(photolist),
                callback_prefix={
                    "page": f"{config.EVENT_PHOTOS_CALLBACK_PATTERN}{event_type}_",
                    "submit": f"{config.SUBMIT_PHOTO_CALLBACK_PATTERN}{event_type}_{current_photo_index}"
                }
            )
        )
        return True
    else:
        await send_text_response(
            update,
            context,
            "Список фотографий пуст"
        )
        return False


async def edit_event_photo_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    current_photo_index = get_id(query.data)
    event_type = get_prev_callback(query.data)
    photo_path = config.EVENT_PHOTOS_DIR / event_type
    photolist = [photo for photo in photo_path.iterdir() if photo.is_file()]
    await query.edit_message_media(
        InputMediaPhoto(
            media=open(photolist[current_photo_index], "rb")
        ),
        reply_markup=get_photolist_keyboard(
            current_photo_index=current_photo_index,
            photo_count=len(photolist),
            callback_prefix={
                "page": f"{config.EVENT_PHOTOS_CALLBACK_PATTERN}{event_type}_",
                "submit": f"{config.SUBMIT_PHOTO_CALLBACK_PATTERN}{event_type}_{current_photo_index}"
            }
        )
    )
