from telegram import Update
from telegram.ext import ContextTypes

from mafia_bot.handlers.response import send_response
from mafia_bot.templates import render_template


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_response(update, context, response=render_template("info.j2"))
