from telegram import Update
from telegram.ext import ContextTypes

from mafia_bot.handlers.response import send_response, send_response_photo
from mafia_bot.templates import render_template


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_response_photo(update, context, response=render_template("start.j2"))
