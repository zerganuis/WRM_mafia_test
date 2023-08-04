import enum

from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler
)

from mafia_bot import config
from mafia_bot.handlers.response import send_text_response
from mafia_bot.templates import render_template
from mafia_bot.services.event import (
    insert_event_id,
    get_max_event_id,
    update_event_parameter,
    delete_event,
    delete_event_edit,
    get_edit_event_id,
    format_datetime_to_db
)
from mafia_bot.services.user import (
    validate_user,
    AccessLevel,
    get_user_by_id
)
from mafia_bot.handlers.edit_event_photo import reg_event_photo
from mafia_bot.handlers.events import _edit_event_photo, CallbackQueryHandler
from mafia_bot.handlers.keyboards import get_delete_photo_type_keyboard
from mafia_bot.handlers.menu import get_prev_callback

template_prefix = config.REGEVENT_TEMPLATES_DIR


class EventRegistrationState(enum.Enum):
    TYPE: 'EventRegistrationState' = 0
    NAME: 'EventRegistrationState' = 1
    DATETIME: 'EventRegistrationState' = 2
    PLACE: 'EventRegistrationState' = 3
    HOST: 'EventRegistrationState' = 4
    COST: 'EventRegistrationState' = 5
    DESCRIPTION: 'EventRegistrationState' = 6
    PHOTO: 'EventRegistrationState' = 7


@validate_user(AccessLevel.ADMIN)
async def cmd_regevent(update: Update, context: ContextTypes.DEFAULT_TYPE, access_level) -> EventRegistrationState:
    if not update.message:
        return
    max_id = await get_max_event_id()
    user_id = update.effective_user.id
    if not max_id:
        max_id = 0
    await insert_event_id(user_id, max_id + 1)
    await send_text_response(
        update,
        context,
        render_template(
            f"{template_prefix}get_type.j2"
        ),
        get_delete_photo_type_keyboard({
            "Мафия": f"{config.REG_EVENT_TYPE_CALLBACK_PATTERN}mafia_0",
            "Денежный поток": f"{config.REG_EVENT_TYPE_CALLBACK_PATTERN}flow_0",
            "Бункер": f"{config.REG_EVENT_TYPE_CALLBACK_PATTERN}bunker_0"
        })
    )
    return EventRegistrationState.TYPE


async def _get_event_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> EventRegistrationState:
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    user_id = update.effective_user.id
    event_id = await get_edit_event_id(user_id)
    event_type = get_prev_callback(query.data)
    await update_event_parameter(event_id, "type", event_type)
    await send_text_response(
        update,
        context,
        render_template(f"{template_prefix}get_name.j2")
    )
    return EventRegistrationState.NAME


async def _get_event_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> EventRegistrationState:
    user_id = update.effective_user.id
    event_id = await get_edit_event_id(user_id)
    text = update.message.text
    await update_event_parameter(event_id, "name", text)
    await send_text_response(
        update,
        context,
        render_template(f"{template_prefix}get_datetime.j2")
    )
    return EventRegistrationState.DATETIME


async def _get_event_datetime(update: Update, context: ContextTypes.DEFAULT_TYPE) -> EventRegistrationState:
    user_id = update.effective_user.id
    event_id = await get_edit_event_id(user_id)
    text = update.message.text
    try:
        param_value = f"datetime('{format_datetime_to_db(text)}')"
    except Exception:
        await send_text_response(
            update,
            context,
            "Вы неверно ввели дату, попробуйте еще раз:"
        )
        return EventRegistrationState.DATETIME
    await update_event_parameter(event_id, "datetime", param_value)
    await send_text_response(
        update,
        context,
        render_template(f"{template_prefix}get_place.j2")
    )
    return EventRegistrationState.PLACE


async def _get_event_place(update: Update, context: ContextTypes.DEFAULT_TYPE) -> EventRegistrationState:
    user_id = update.effective_user.id
    event_id = await get_edit_event_id(user_id)
    text = update.message.text
    await update_event_parameter(event_id, "place", text)
    await send_text_response(
        update,
        context,
        render_template(f"{template_prefix}get_host.j2")
    )
    return EventRegistrationState.HOST


async def _get_event_host(update: Update, context: ContextTypes.DEFAULT_TYPE) -> EventRegistrationState:
    user_id = update.effective_user.id
    host_id = update.message.contact.user_id
    host = await get_user_by_id(host_id)
    if host:
        event_id = await get_edit_event_id(user_id)
    else:
        await send_text_response(
            update,
            context,
            """Этот пользователь не зарегистрирован, 
ведущим может быть только зарегистрированный пользователь. 
Введите контакт ведущего заново:"""
        )
        return EventRegistrationState.HOST
    text = update.message.text
    await update_event_parameter(event_id, "host_id", host_id)
    await send_text_response(
        update,
        context,
        render_template(f"{template_prefix}get_cost.j2")
    )
    return EventRegistrationState.COST


async def _get_event_cost(update: Update, context: ContextTypes.DEFAULT_TYPE) -> EventRegistrationState:
    user_id = update.effective_user.id
    event_id = await get_edit_event_id(user_id)
    text = update.message.text
    await update_event_parameter(event_id, "cost", text)
    await send_text_response(
        update,
        context,
        render_template(f"{template_prefix}get_description.j2")
    )
    return EventRegistrationState.DESCRIPTION


async def _get_event_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> EventRegistrationState:
    user_id = update.effective_user.id
    event_id = await get_edit_event_id(user_id)
    text = update.message.text
    await update_event_parameter(event_id, "description", text)
    await reg_event_photo(update, context)
    return EventRegistrationState.PHOTO


async def _cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    event_id = await get_edit_event_id(user_id)
    await delete_event(event_id)
    await delete_event_edit(event_id)
    await send_text_response(
        update,
        context,
        render_template("cancel.j2")
    )
    return ConversationHandler.END


def get_regevent_conversation() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("regevent", cmd_regevent)],
        states={
            EventRegistrationState.TYPE: [
                CallbackQueryHandler(
                    _get_event_type,
                    pattern=rf"^{config.REG_EVENT_TYPE_CALLBACK_PATTERN}(.+)$"
                ),
                # MessageHandler(filters.TEXT & ~filters.COMMAND, _get_event_type)
            ],
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
            EventRegistrationState.PHOTO: [
                CallbackQueryHandler(
                    _edit_event_photo,
                    pattern=rf"^{config.SUBMIT_PHOTO_CALLBACK_PATTERN}(.+)$"
                )
            ],
        },
        fallbacks=[MessageHandler(filters.COMMAND, _cancel)],
    )
