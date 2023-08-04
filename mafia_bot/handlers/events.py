from datetime import timedelta, datetime

import telegram
from telegram import Update, InputMediaPhoto
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from mafia_bot import config
from mafia_bot.handlers.response import send_text_response, send_photos_response
from mafia_bot.handlers.keyboards import (
    get_event_profile_keyboard,
    get_edit_event_profile_keyboard,
    get_element_list_keyboard,
    get_delete_photo_type_keyboard
)
from mafia_bot.templates import render_template
from mafia_bot.services.event import (
    update_event_parameter,
    sign_up,
    is_signed_up,
    format_datetime_to_db,
    insert_event_edit,
    get_edit_event_id,
    delete_event_edit,
    sign_out
)
from mafia_bot.services.user import get_user_by_id, validate_user, AccessLevel
from mafia_bot.services.eventlist import get_eventlist
from mafia_bot.handlers.menu import get_id, get_prev_callback
from mafia_bot.services.event import get_event_by_id
from mafia_bot.services.userlist import get_event_participants
from mafia_bot.handlers.edit_event_photo import edit_event_photo


### Events command

@validate_user(AccessLevel.USER)
async def cmd_events(update: Update, context: ContextTypes.DEFAULT_TYPE, access_level: AccessLevel):
    if not update.message:
        return
    period = timedelta(0)
    eventlist = await get_eventlist(period)
    await send_photos_response(
        update,
        context,
        render_template("events.j2"),
        get_element_list_keyboard(
            eventlist[0],
            callback_prefix={
                "element_list": config.EVENTS_CALLBACK_PATTERN,
                "element": f"{config.EVENT_PROFILE_CALLBACK_PATTERN}{config.EVENTS_CALLBACK_PATTERN}0_"
            },
            page_count=len(eventlist),
            current_page_index=0,
            get_name=lambda event: f"{event.name}"
        )
    )


async def eventlist_page_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    period = timedelta(0)
    eventlist = await get_eventlist(period)
    current_page_index = get_id(query.data)
    if current_page_index == 0:
        await query.edit_message_media(
            InputMediaPhoto(
                media=open(config.BASE_PHOTO, 'rb'),
                caption=render_template("events.j2"),
                parse_mode=telegram.constants.ParseMode.HTML,
            ),
            reply_markup=get_element_list_keyboard(
                eventlist[current_page_index],
                callback_prefix={
                    "element_list": config.EVENTS_CALLBACK_PATTERN,
                    "element": f"{config.EVENT_PROFILE_CALLBACK_PATTERN}{config.EVENTS_CALLBACK_PATTERN}0_"
                },
                page_count=len(eventlist),
                current_page_index=current_page_index,
                get_name=lambda event: f"{event.name}"
            )
        )
    else:
        await query.edit_message_caption(
            caption=render_template("events.j2"),
            reply_markup=get_element_list_keyboard(
                eventlist[current_page_index],
                callback_prefix={
                    "element_list": config.EVENTS_CALLBACK_PATTERN,
                    "element": f"{config.EVENT_PROFILE_CALLBACK_PATTERN}{config.EVENTS_CALLBACK_PATTERN}0_"
                },
                page_count=len(eventlist),
                current_page_index=current_page_index,
                get_name=lambda event: f"{event.name}"
            ),
            parse_mode=telegram.constants.ParseMode.HTML,
        )


### Event profile

@validate_user(AccessLevel.USER)
async def event_profile_button(update: Update, context: ContextTypes.DEFAULT_TYPE, access_level: AccessLevel):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    prev_callback = get_prev_callback(query.data)
    event_id = get_id(query.data)
    current_event = await get_event_by_id(event_id)
    host = await get_user_by_id(current_event.host_id)
    participants = await get_event_participants(event_id)
    participant_list = []
    for page in participants:
        for user in page:
            participant_list.append(user)
    callback_prefix = {
        "back": prev_callback,
        "participants": {
            "count": len(participant_list),
            "callback": f"{config.EVENT_PARTICIPANTS_CALLBACK_PATTERN}{query.data}_0"
        },
        "host_profile": config.HOST_PROFILE_CALLBACK_PATTERN
    }
    if current_event.datetime > datetime.now():
        callback_prefix["sign_up"] = f"{config.EVENT_SIGN_UP_CALLBACK_PATTERN}{query.data}_{current_event.id}"
    if access_level == AccessLevel.ADMIN:
        callback_prefix["edit"] = f"{config.EDIT_EVENT_PROFILE_CALLBACK_PATTERN}{query.data}_{current_event.id}"
    user_id = query.from_user.id
    isSignedUp = await is_signed_up(user_id, current_event.id)
    await query.edit_message_media(
        InputMediaPhoto(
            media=open(current_event.picture, 'rb'),
            caption=render_template(
                "event.j2",
                {
                    "event": current_event,
                    "datetime": current_event.datetime.strftime(config.DATETIME_FORMAT),
                    "host": host
                },
            ),
            parse_mode=telegram.constants.ParseMode.HTML,
        ),
        reply_markup=get_event_profile_keyboard(
            callback_prefix=callback_prefix,
            is_signed_up=isSignedUp
        )
    )


### Sign Up Button

@validate_user(AccessLevel.USER)
async def sign_up_button(update: Update, context: ContextTypes.DEFAULT_TYPE, access_level: AccessLevel):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    prev_callback = get_prev_callback(query.data)
    back_callback = get_prev_callback(prev_callback)
    event_id = get_id(query.data)
    current_event = await get_event_by_id(event_id)
    user_id = query.from_user.id
    isSignedUp = await is_signed_up(user_id, current_event.id)
    if isSignedUp:
        await sign_out(user_id, current_event.id)
    else:
        await sign_up(user_id, current_event.id)
    isSignedUp = not isSignedUp

    host = await get_user_by_id(current_event.host_id)
    participants = await get_event_participants(event_id)
    participant_list = []
    for page in participants:
        for user in page:
            participant_list.append(user)
    callback_prefix = {
        "back": back_callback,
        "participants": {
            "count": len(participant_list),
            "callback": f"{config.EVENT_PARTICIPANTS_CALLBACK_PATTERN}{prev_callback}_0"
        },
        "host_profile": config.HOST_PROFILE_CALLBACK_PATTERN
    }
    if current_event.datetime > datetime.now():
        callback_prefix["sign_up"] = f"{config.EVENT_SIGN_UP_CALLBACK_PATTERN}{prev_callback}_{current_event.id}"
    if access_level == AccessLevel.ADMIN:
        callback_prefix["edit"] = f"{config.EDIT_EVENT_PROFILE_CALLBACK_PATTERN}{prev_callback}_{current_event.id}"
    await query.edit_message_caption(
        caption=render_template(
            "event.j2",
            {
                "event": current_event,
                "datetime": current_event.datetime.strftime(config.DATETIME_FORMAT),
                "host": host
            },
        ),
        reply_markup=get_event_profile_keyboard(
            callback_prefix=callback_prefix,
            is_signed_up=isSignedUp
        )
    )
    await send_text_response(
        update,
        context,
        render_template(
            "sign_up.j2",
            {"isSignedUp": isSignedUp}
        )
    )


### Edit Event Profile

async def edit_event_profile_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    prev_callback = get_prev_callback(query.data)
    event_id = get_id(query.data)
    edit_parameters = {
        'name': 'Название',
        'datetime': 'Дата и время',
        'place': 'Место',
        'host_id': 'Ведущий',
        'cost': 'Стоимость',
        'description': 'Описание',
        'photo': 'Фото',
        'type': 'Тип'
    }
    await query.edit_message_caption(
        caption=render_template(
            "edit_profile_menu.j2"
        ),
        reply_markup=get_edit_event_profile_keyboard(
            edit_parameters,
            event_id,
            {
                "prefix": config.EDIT_EVENT_PARAMETER_CALLBACK_PATTERN,
                "back": prev_callback
            }
        ),
        parse_mode=telegram.constants.ParseMode.HTML,
    )


async def edit_event_parameter_start_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    event_id = get_id(query.data)
    user_id = update.effective_user.id
    await insert_event_edit(user_id, event_id)
    param_name = get_prev_callback(query.data)
    if param_name == 'photo':
        hasPhotos = await edit_event_photo(update, context)
        return param_name if hasPhotos else ConversationHandler.END
    elif param_name == 'type':
        await query.edit_message_caption(
            caption="Выберите тип мероприятия:",
            reply_markup=get_delete_photo_type_keyboard({
                "Мафия": f"{config.EDIT_EVENT_TYPE_CALLBACK_PATTERN}mafia_0",
                "Денежный поток": f"{config.EDIT_EVENT_TYPE_CALLBACK_PATTERN}flow_0",
                "Бункер": f"{config.EDIT_EVENT_TYPE_CALLBACK_PATTERN}bunker_0"
            }),
            parse_mode=telegram.constants.ParseMode.HTML,
        )
        return param_name
    template = "edit_parameter_base.j2"
    if param_name == "datetime":
        template = "edit_parameter_datetime.j2"
    await query.edit_message_caption(
        caption=render_template(template),
        parse_mode=telegram.constants.ParseMode.HTML,
    )
    return param_name


async def edit_event_parameter(update: Update, context: ContextTypes.DEFAULT_TYPE, param_name: str):
    user_id = update.effective_user.id
    event_id = await get_edit_event_id(user_id)
    if param_name == 'datetime':
        try:
            param_value = f"datetime('{format_datetime_to_db(param_value)}')"
        except Exception:
            await send_text_response(
                update,
                context,
                "Вы неверно ввели дату, попробуйте еще раз:"
            )
            return "datetime"
    elif param_name == 'host_id':
        host_id = update.message.contact.user_id
        host = await get_user_by_id(host_id)
        if host:
            param_value = host_id
        else:
            await send_text_response(
                update,
                context,
                """Этот пользователь не зарегистрирован, 
ведущим может быть только зарегистрированный пользователь. 
Введите контакт ведущего заново:"""
            )
            return "host_id"
    elif param_name == 'picture':
        query = update.callback_query
        event = await get_event_by_id(event_id)
        event_type = get_prev_callback(query.data)
        photo_path = config.EVENT_PHOTOS_DIR / event_type
        photolist = [photo.name for photo in photo_path.iterdir() if photo.is_file()]
        photo_id = get_id(query.data)
        param_value = config.EVENT_PHOTOS_DIR / event.event_type / f"{photolist[photo_id]}"
    elif param_name == 'type':
        query = update.callback_query
        param_value = get_prev_callback(query.data)
    else:
        param_value = update.message.text
    await update_event_parameter(event_id, param_name, param_value)
    await delete_event_edit(event_id)
    await send_text_response(
        update,
        context,
        render_template("done.j2")
    )
    return ConversationHandler.END


async def _edit_event_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await edit_event_parameter(update, context, "type")


async def _edit_event_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await edit_event_parameter(update, context, "name")


async def _edit_event_datetime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await edit_event_parameter(update, context, "datetime")


async def _edit_event_place(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await edit_event_parameter(update, context, "place")


async def _edit_event_cost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await edit_event_parameter(update, context, "cost")


async def _edit_event_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await edit_event_parameter(update, context, "description")


async def _edit_event_host_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await edit_event_parameter(update, context, "host_id")

async def _edit_event_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await edit_event_parameter(update, context, "picture")


async def _cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    event_id = await get_edit_event_id(user_id)
    await delete_event_edit(event_id)
    await send_text_response(
        update,
        context,
        render_template("cancel.j2")
    )
    return ConversationHandler.END


def get_edit_event_conversation() -> ConversationHandler:
    pattern = rf"^{config.EDIT_EVENT_PARAMETER_CALLBACK_PATTERN}(.+)$"
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_event_parameter_start_button, pattern=pattern)],
        states={
            "type": [
                CallbackQueryHandler(
                    _edit_event_type,
                    pattern=rf"^{config.EDIT_EVENT_TYPE_CALLBACK_PATTERN}(.+)$"
                )
                # MessageHandler(filters.TEXT & ~filters.COMMAND, _edit_event_type)
                ],
            "name": [MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                _edit_event_name
                )],
            "datetime": [MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                _edit_event_datetime
                )],
            "place": [MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                _edit_event_place
                )],
            "cost": [MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                _edit_event_cost
                )],
            "description": [MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                _edit_event_description
                )],
            "host_id": [MessageHandler(
                filters.CONTACT,
                _edit_event_host_id
                )],
            "photo": [CallbackQueryHandler(
                _edit_event_photo,
                pattern=rf"^{config.SUBMIT_PHOTO_CALLBACK_PATTERN}(.+)$"
                )]
        },
        fallbacks=[MessageHandler(filters.COMMAND, _cancel)]
    )


### Event Participants

async def event_participants_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    current_page_index = get_id(query.data)
    prev_callback = get_prev_callback(query.data)
    event_id = get_id(prev_callback)
    event = await get_event_by_id(event_id)
    participants = await get_event_participants(event_id)
    if not participants:
        await send_text_response(
            update,
            context,
            render_template("no_participants.j2")
        )
        return
    await query.edit_message_media(
        InputMediaPhoto(
            media=open(event.picture, 'rb'),
            caption=render_template("event_participants.j2"),
            parse_mode=telegram.constants.ParseMode.HTML,
        ),
        reply_markup=get_element_list_keyboard(
            participants[current_page_index],
            callback_prefix={
                "element_list": f"{config.EVENT_PARTICIPANTS_CALLBACK_PATTERN}{prev_callback}_",
                "element": f"{config.USER_PROFILE_CALLBACK_PATTERN}{query.data}_",
                "back": prev_callback
            },
            page_count=len(participants),
            current_page_index=current_page_index,
            get_name=lambda user: f"{user.nickname}"
        )
    )
