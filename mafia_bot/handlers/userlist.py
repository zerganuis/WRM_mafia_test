import telegram
from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes


from mafia_bot import config
from mafia_bot.handlers.response import send_photos_response
from mafia_bot.handlers.keyboards import get_element_list_keyboard
from mafia_bot.templates import render_template
from mafia_bot.services.user import validate_user, AccessLevel
from mafia_bot.services.userlist import get_userlist
from mafia_bot.handlers.menu import get_id


@validate_user(AccessLevel.ADMIN)
async def cmd_userlist(update: Update, context: ContextTypes.DEFAULT_TYPE, access_level: AccessLevel):
    if not update.message:
        return
    userlist = await get_userlist()
    await send_photos_response(
        update,
        context,
        render_template("userlist.j2"),
        get_element_list_keyboard(
            userlist[0],
            callback_prefix={
                "element_list": config.USERLIST_CALLBACK_PATTERN,
                "element": f"{config.USER_PROFILE_CALLBACK_PATTERN}{config.USERLIST_CALLBACK_PATTERN}0_"
            },
            page_count=len(userlist),
            current_page_index=0,
            get_name=lambda user: f"{user.name} ({user.nickname})"
        )
    )


async def userlist_page_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    userlist = await get_userlist()
    current_page_index = get_id(query.data)
    await query.edit_message_media(
        InputMediaPhoto(
            media=open(config.BASE_PHOTO, 'rb'),
            caption=render_template("userlist.j2"),
            parse_mode=telegram.constants.ParseMode.HTML,
        ),
        reply_markup=get_element_list_keyboard(
            userlist[current_page_index],
            callback_prefix={
                "element_list": config.USERLIST_CALLBACK_PATTERN,
                "element": f"{config.USER_PROFILE_CALLBACK_PATTERN}{config.USERLIST_CALLBACK_PATTERN}0_0"
            },
            page_count=len(userlist),
            current_page_index=current_page_index,
            get_name=lambda user: f"{user.name} ({user.nickname})"
        )
    )
