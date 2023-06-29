import datetime

import telegram
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from mafia_bot import config
from mafia_bot.handlers.response import send_response
from mafia_bot.handlers.keyboards import get_eventlist_keyboard, get_event_keyboard
from mafia_bot.templates import render_template
from mafia_bot.services.user import get_userlist, get_top_users


async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _top_alltime(update, context)
    await _top_month(update, context)


async def _top_alltime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    month = datetime.timedelta(days=0)
    users = list(await get_top_users(month))
    if not update.message:
        return
    await send_response(
        update,
        context,
        render_template(
            "userlist.j2",
            {"period": "За все время", "userlist": users}
        )
    )

async def _top_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    month = datetime.timedelta(days=30)
    users = list(await get_top_users(month))
    if not update.message:
        return
    await send_response(
        update,
        context,
        render_template(
            "userlist.j2",
            {"period": "За последние 30 дней", "userlist": users}
        )
    )