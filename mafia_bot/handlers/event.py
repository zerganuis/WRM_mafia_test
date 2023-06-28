import datetime
import telegram
from telegram import Update
from telegram.ext import ContextTypes

from mafia_bot import config
from mafia_bot.handlers.response import send_response
from mafia_bot.templates import render_template
from mafia_bot.handlers.keyboards import get_event_keyboard
from mafia_bot.services.events import Event


async def event(query):
    current_event = _get_current_event(query.data)
    await query.edit_message_text(
        text=render_template(
            "event.j2",
            {"name": current_event.name},
        ),
        reply_markup=get_event_keyboard(
            callback_prefix=config.INTO_EVENT_CALLBACK_PATTERN
        ),
        parse_mode=telegram.constants.ParseMode.HTML,
    )

def _get_current_event(query_data):
    return Event(
        id=100,
        name="test_name",
        date=datetime.datetime.now(),
        place="ТУТ",
        members=[
            1, 2, 3, 4, 5
        ],
        ordering=5
    )
