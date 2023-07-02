import telegram
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from mafia_bot import config
from mafia_bot.handlers.response import send_response
from mafia_bot.handlers.keyboards import (
    get_eventlist_keyboard,
    get_event_profile_keyboard,
    get_edit_event_profile_keyboard
)
from mafia_bot.templates import render_template
from mafia_bot.services.event import (
    get_eventlist,
    get_event,
    update_event_parameter
)
from mafia_bot.services.user import get_user_by_id


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
                "userlist": f"{config.USERLIST_CALLBACK_PATTERN}{query.data}",
                "edit": f"{config.EDIT_EVENT_PROFILE_CALLBACK_PATTERN}{current_event.id}",
                "sign_up": f" "
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

###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################

async def edit_event_profile_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    event_id = _get_event_id(query.data)
    await query.edit_message_text(
        text=render_template(
            "edit_profile_menu.j2"
        ),
        reply_markup=get_edit_event_profile_keyboard(
            {
                "name": f"{config.EDIT_EVENT_PROFILE_CALLBACK_PATTERN[:-1]}.name_{event_id}",
                "datetime": f"{config.EDIT_EVENT_PROFILE_CALLBACK_PATTERN[:-1]}.datetime_{event_id}",
                "place": f"{config.EDIT_EVENT_PROFILE_CALLBACK_PATTERN[:-1]}.place_{event_id}",
                "host": f"{config.EDIT_EVENT_PROFILE_CALLBACK_PATTERN[:-1]}.host_{event_id}",
                "back": f"{config.EVENT_PROFILE_CALLBACK_PATTERN}{event_id}"
            }
        ),
        parse_mode=telegram.constants.ParseMode.HTML,
    )


def _get_event_id(query_data: str) -> str:
    pattern_prefix_length = len(config.EDIT_EVENT_PROFILE_CALLBACK_PATTERN)
    return int(query_data[pattern_prefix_length:])


async def edit_event_parameter_start_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    param_name = _get_param_name(query.data)
    print(param_name)
    template = "edit_parameter_base.j2"
    if param_name == "datetime":
        template = "edit_parameter_datetime.j2"
    await query.edit_message_text(
        text=render_template(
            template
        ),
        parse_mode=telegram.constants.ParseMode.HTML,
    )
    return param_name


def _get_param_name(query_data: str) -> str:
    pattern_prefix_length = len(config.EDIT_EVENT_PROFILE_CALLBACK_PATTERN)
    pattern_postfix_length = query_data.rfind("_")
    param_name = query_data[pattern_prefix_length:pattern_postfix_length]
    return param_name


async def edit_event_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    event_id = update.message.from_user.id
    param_value = update.message.text
    await update_event_parameter("name", param_value, event_id)
    await send_response(
        update,
        context,
        render_template("done.j2")
    )
    return ConversationHandler.END


async def edit_event_datetime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    event_id = update.message.from_user.id
    param_value = update.message.text
    await update_event_parameter("datetime", param_value, event_id)
    await send_response(
        update,
        context,
        render_template("done.j2")
    )
    return ConversationHandler.END


async def edit_event_place(update: Update, context: ContextTypes.DEFAULT_TYPE):
    event_id = update.message.from_user.id
    param_value = update.message.text
    await update_event_parameter("place", param_value, event_id)
    await send_response(
        update,
        context,
        render_template("done.j2")
    )
    return ConversationHandler.END


async def edit_event_host(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    param_value = update.message.text
    await send_response(
        update,
        context,
        render_template("done.j2")
    )
    return ConversationHandler.END


async def _cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await send_response(
        update,
        context,
        render_template("cancel.j2")
    )
    return ConversationHandler.END


def get_edit_event_conversation() -> ConversationHandler:
    pattern = rf"^{config.EDIT_EVENT_PROFILE_CALLBACK_PATTERN[:-1]}\.(.+)$"
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_event_parameter_start_button, pattern=pattern)],
        states={
            "name": [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_event_name)],
            "datetime": [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_event_datetime)],
            "place": [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_event_place)],
            "host": [MessageHandler(filters.PHOTO, edit_event_host)]
        },
        fallbacks=[MessageHandler(filters.COMMAND, _cancel)]
    )

