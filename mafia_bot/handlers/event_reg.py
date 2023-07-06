from collections.abc import Iterable
import enum

import telegram
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from mafia_bot import config
from mafia_bot.handlers.response import send_response
from mafia_bot.templates import render_template
from mafia_bot.services.event import (
    Event,
    insert_event_id,
    get_max_event_id,
    update_event_parameter,
    delete_event,
    delete_event_registration,
    get_reg_event_id,
    format_datetime
)
from mafia_bot.services.user import (
    User,
    validate_user,
    AccessLevel
)

template_prefix = "event_reg/"


class EventRegistrationState(enum.Enum):
    NAME: 'EventRegistrationState' = 0
    DATETIME: 'EventRegistrationState' = 1
    PLACE: 'EventRegistrationState' = 2
    HOST: 'EventRegistrationState' = 3
    COST: 'EventRegistrationState' = 4
    DESCRIPTION: 'EventRegistrationState' = 5


@validate_user(AccessLevel.ADMIN)
async def create_event(update: Update, context: ContextTypes.DEFAULT_TYPE, access_level) -> EventRegistrationState:
    if not update.message:
        return
    max_id = await get_max_event_id()
    user_id = update.effective_user.id
    await insert_event_id(user_id, max_id + 1)
    await send_response(
        update,
        context,
        render_template(
            f"{template_prefix}reg_start.j2"
        )
    )
    return EventRegistrationState.NAME


async def _get_event_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> EventRegistrationState:
    user_id = update.effective_user.id
    event_id = await get_reg_event_id(user_id)
    text = update.message.text
    await update_event_parameter(
        "name",
        text,
        event_id
    )
    await send_response(
        update,
        context,
        render_template(
            f"{template_prefix}get_event_name.j2"
        )
    )
    return EventRegistrationState.DATETIME


async def _get_event_datetime(update: Update, context: ContextTypes.DEFAULT_TYPE) -> EventRegistrationState:
    user_id = update.effective_user.id
    event_id = await get_reg_event_id(user_id)
    text = update.message.text
    await update_event_parameter(
        "datetime",
        f"datetime('{format_datetime(text)}')",
        event_id
    )
    await send_response(
        update,
        context,
        render_template(
            f"{template_prefix}get_event_datetime.j2"
        )
    )
    return EventRegistrationState.PLACE


async def _get_event_place(update: Update, context: ContextTypes.DEFAULT_TYPE) -> EventRegistrationState:
    user_id = update.effective_user.id
    event_id = await get_reg_event_id(user_id)
    text = update.message.text
    await update_event_parameter(
        "place",
        text,
        event_id
    )
    await send_response(
        update,
        context,
        render_template(
            f"{template_prefix}get_event_place.j2"
        )
    )
    return EventRegistrationState.HOST


async def _get_event_host(update: Update, context: ContextTypes.DEFAULT_TYPE) -> EventRegistrationState:
    user_id = update.effective_user.id
    event_id = await get_reg_event_id(user_id)
    text = update.message.text
    await update_event_parameter(
        "host_id",
        update.message.contact.user_id,
        event_id
    )
    await send_response(
        update,
        context,
        render_template(
            f"{template_prefix}get_event_host.j2"
        )
    )
    return EventRegistrationState.COST


async def _get_event_cost(update: Update, context: ContextTypes.DEFAULT_TYPE) -> EventRegistrationState:
    user_id = update.effective_user.id
    event_id = await get_reg_event_id(user_id)
    text = update.message.text
    await update_event_parameter(
        "cost",
        text,
        event_id
    )
    await send_response(
        update,
        context,
        render_template(
            f"{template_prefix}get_event_cost.j2"
        )
    )
    return EventRegistrationState.DESCRIPTION


async def _get_event_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> EventRegistrationState:
    user_id = update.effective_user.id
    event_id = await get_reg_event_id(user_id)
    text = update.message.text
    await update_event_parameter(
        "description",
        text,
        event_id
    )
    await delete_event_registration(event_id)
    await send_response(
        update,
        context,
        render_template(
            f"{template_prefix}get_event_description.j2"
        )
    )
    return ConversationHandler.END


async def _cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    event_id = await get_reg_event_id(user_id)
    await delete_event(event_id)
    await delete_event_registration(event_id)
    await send_response(
        update,
        context,
        render_template("cancel.j2")
    )
    return ConversationHandler.END


def get_regevent_conversation() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("regevent", create_event)],
        states={
            EventRegistrationState.NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, _get_event_name)
            ],
            EventRegistrationState.DATETIME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, _get_event_datetime)
            ],
            EventRegistrationState.PLACE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, _get_event_place)
            ],
            EventRegistrationState.HOST: [
                MessageHandler(filters.CONTACT, _get_event_host)
            ],
            EventRegistrationState.COST: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, _get_event_cost)
            ],
            EventRegistrationState.DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, _get_event_description)
            ],
        },
        fallbacks=[MessageHandler(filters.COMMAND, _cancel)],
    )
