import telegram
from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes

from mafia_bot import config
from mafia_bot.handlers.response import send_photos_response
from mafia_bot.handlers.keyboards import get_element_list_keyboard
from mafia_bot.templates import render_template
from mafia_bot.services.user import validate_user, AccessLevel
from mafia_bot.services.eventlist import get_eventlist
from mafia_bot.handlers.menu import get_id


### Events command

@validate_user(AccessLevel.ADMIN)
async def cmd_allevents(update: Update, context: ContextTypes.DEFAULT_TYPE, access_level: AccessLevel):
    if not update.message:
        return
    eventlist = await get_eventlist(isDescendingOrder=True)
    await send_photos_response(
        update,
        context,
        render_template("events.j2"),
        get_element_list_keyboard(
            eventlist[0],
            callback_prefix={
                "element_list": config.ALLEVENTS_CALLBACK_PATTERN,
                "element": f"{config.EVENT_PROFILE_CALLBACK_PATTERN}{config.ALLEVENTS_CALLBACK_PATTERN}0_"
            },
            page_count=len(eventlist),
            current_page_index=0,
            get_name=lambda event: f"{event.name}"
        )
    )

async def alleventlist_page_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    eventlist = await get_eventlist(isDescendingOrder=True)
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
                    "element_list": config.ALLEVENTS_CALLBACK_PATTERN,
                    "element": f"{config.EVENT_PROFILE_CALLBACK_PATTERN}{config.ALLEVENTS_CALLBACK_PATTERN}0_"
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
                    "element_list": config.ALLEVENTS_CALLBACK_PATTERN,
                    "element": f"{config.EVENT_PROFILE_CALLBACK_PATTERN}{config.ALLEVENTS_CALLBACK_PATTERN}0_"
                },
                page_count=len(eventlist),
                current_page_index=current_page_index,
                get_name=lambda event: f"{event.name}"
            ),
            parse_mode=telegram.constants.ParseMode.HTML,
        )
