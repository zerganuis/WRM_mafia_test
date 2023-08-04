from telegram import Update
from telegram.ext import ContextTypes

from mafia_bot.handlers.response import send_photos_response
from mafia_bot.templates import render_template


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_photos_response(
        update,
        context,
        caption=render_template("start.j2"))
