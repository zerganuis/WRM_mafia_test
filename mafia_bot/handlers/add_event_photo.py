
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    CommandHandler
)

from mafia_bot import config
from mafia_bot.handlers.response import send_text_response, send_photos_response
from mafia_bot.templates import render_template
from mafia_bot.handlers.menu import get_prev_callback
from mafia_bot.handlers.keyboards import get_delete_photo_type_keyboard
from mafia_bot.services.user import validate_user, AccessLevel


@validate_user(AccessLevel.ADMIN)
async def cmd_addphoto(update: Update, context: ContextTypes.DEFAULT_TYPE, access_level: AccessLevel):
    if not update.message:
        return
    await send_photos_response(
        update,
        context,
        render_template("addphoto.j2"),
        get_delete_photo_type_keyboard({
            "Мафия": f"{config.ADD_PHOTO_CALLBACK_PATTERN}mafia_0",
            "Денежный поток": f"{config.ADD_PHOTO_CALLBACK_PATTERN}flow_0",
            "Бункер": f"{config.ADD_PHOTO_CALLBACK_PATTERN}bunker_0",
            "Команда /info": f"{config.ADD_PHOTO_CALLBACK_PATTERN}info_0",
        })
    )
    return "type"


async def _choose_event_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    event_type = get_prev_callback(query.data)
    await send_text_response(
        update,
        context,
        "Отправьте фото:"
    )
    return event_type


async def _add_photo(update: Update, context: ContextTypes.DEFAULT_TYPE, event_type: str):
    photo_file = await update.message.photo[-1].get_file()
    photo_path = config.EVENT_PHOTOS_DIR / event_type
    if event_type == "info":
        photo_path = config.INFO_PHOTOS_DIR
    photolist = [photo.name for photo in photo_path.iterdir() if photo.is_file()]
    photo_name = len(photolist)
    while f"{photo_name}.jpg" in photolist:
        photo_name += 1
    path = photo_path / f"{photo_name}.jpg"
    await photo_file.download_to_drive(custom_path=path)
    await send_text_response(
        update,
        context,
        render_template("done.j2")
    )
    return ConversationHandler.END


async def _add_mafia_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await _add_photo(update, context, "mafia")


async def _add_bunker_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await _add_photo(update, context, "bunker")


async def _add_flow_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await _add_photo(update, context, "flow")


async def _add_info_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await _add_photo(update, context, "info")


async def _cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await send_text_response(
        update,
        context,
        render_template("cancel.j2")
    )
    return ConversationHandler.END


def add_event_photo_conversation() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("addphoto", cmd_addphoto)],
        states={
            "type": [CallbackQueryHandler(
                callback=_choose_event_type,
                pattern=rf"^{config.ADD_PHOTO_CALLBACK_PATTERN}(.+)$"
                )],
            "mafia": [MessageHandler(
                filters.PHOTO,
                _add_mafia_photo
                )],
            "bunker": [MessageHandler(
                filters.PHOTO,
                _add_bunker_photo
                )],
            "flow": [MessageHandler(
                filters.PHOTO,
                _add_flow_photo
                )],
            "info": [MessageHandler(
                filters.PHOTO,
                _add_info_photo
                )],
        },
        fallbacks=[MessageHandler(filters.COMMAND, _cancel)]
    )
