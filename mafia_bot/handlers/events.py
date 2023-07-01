import telegram
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from mafia_bot import config
from mafia_bot.handlers.response import send_response
from mafia_bot.handlers.keyboards import get_eventlist_keyboard, get_event_profile_keyboard
from mafia_bot.templates import render_template
from mafia_bot.services.event import get_eventlist, get_event
from mafia_bot.services.user import get_user_by_id, User


async def eventlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pages_with_events = list(await get_eventlist())
    if not update.message:
        return
    await send_response(
        update,
        context,
        render_template("eventlist.j2"),
        get_eventlist_keyboard(
            pages_with_events[0],
            callback_prefix={
                "eventlist": config.EVENTLIST_CALLBACK_PATTERN,
                "event_profile": config.EVENT_PROFILE_CALLBACK_PATTERN
            },
            page_count=len(pages_with_events),
            current_page_index=0
        )
    )

async def eventlist_page_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    pages_with_events = list(await get_eventlist())
    current_page_index = _get_current_page_index(query.data)
    await query.edit_message_text(
        text=render_template("eventlist.j2"),
        reply_markup=get_eventlist_keyboard(
            pages_with_events[current_page_index],
            callback_prefix={
                "eventlist": config.EVENTLIST_CALLBACK_PATTERN,
                "event_profile": config.EVENT_PROFILE_CALLBACK_PATTERN
            },
            page_count=len(pages_with_events),
            current_page_index=current_page_index,
        ),
        parse_mode=telegram.constants.ParseMode.HTML,
    )

async def event_profile_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    current_event =  await _get_current_event(query.data)
    host = await get_user_by_id(current_event.host_id)
    await query.edit_message_text(
        text=render_template(
            "event.j2",
            {
                "event": current_event,
                "host": host,
                "cost": "1500 рублей"
            },
        ),
        reply_markup=get_event_profile_keyboard(
            callback_prefix={
                "back": config.EVENTLIST_CALLBACK_PATTERN,
                "event_profile": config.EVENT_PROFILE_CALLBACK_PATTERN
            }
        ),
        parse_mode=telegram.constants.ParseMode.HTML,
    )


async def _get_current_event(query_data):
    pattern_prefix_length = len(config.EVENT_PROFILE_CALLBACK_PATTERN)
    event_id = int(query_data[pattern_prefix_length:])
    return await get_event(event_id)


def _get_current_page_index(query_data) -> int:
    pattern_prefix_length = len(config.EVENTLIST_CALLBACK_PATTERN)
    return int(query_data[pattern_prefix_length:])
