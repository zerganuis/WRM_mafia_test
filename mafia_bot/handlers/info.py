from telegram import Update
from telegram.ext import ContextTypes

from mafia_bot import config
from mafia_bot.handlers.response import send_photos_response
from mafia_bot.templates import render_template


async def cmd_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_photos_response(
        update,
        context,
        render_template("info.j2"),
        path_to_photos=config.INFO_PHOTOS_DIR)
