import telegram
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from mafia_bot import config
from mafia_bot.handlers.response import send_response
from mafia_bot.handlers.keyboards import get_page_keyboard, get_events_keyboard
from mafia_bot.templates import render_template
from mafia_bot.services.events import get_all_events
from mafia_bot.handlers.event import event

# async def events(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await send_response(update, context, response=render_template("events.j2"))


async def events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pages_with_events = list(await get_all_events())
    if not update.message:
        return
    await send_response(
        update,
        context,
        render_template(
            "events.j2",
            {"events": pages_with_events[0], "start_index": None},
        ),
        get_events_keyboard(
            pages_with_events[0],
            events_callback_prefix=config.EVENTS_CALLBACK_PATTERN,
            event_callback_prefix=config.EVENT_CALLBACK_PATTERN,
            page_count=len(pages_with_events)
        )
    )

async def all_events_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    pages_with_events = list(await get_all_events())
    if query.data.startswith(config.EVENT_CALLBACK_PATTERN):
        await event(query)
    else:
        await _change_page(query, pages_with_events)

def _get_current_page_index(query_data) -> int:
    pattern_prefix_length = len(config.EVENTS_CALLBACK_PATTERN)
    return int(query_data[pattern_prefix_length:])

async def _change_page(query, pages_with_events):
    current_page_index = _get_current_page_index(query.data)
    await query.edit_message_text(
        text=render_template(
            "events.j2",
            {"events": pages_with_events[current_page_index], "start_index": None},
        ),
        reply_markup=get_events_keyboard(
            pages_with_events[0],
            events_callback_prefix=config.EVENTS_CALLBACK_PATTERN,
            event_callback_prefix=config.EVENT_CALLBACK_PATTERN,
            page_count=len(pages_with_events)
        ),
        parse_mode=telegram.constants.ParseMode.HTML,
    )
