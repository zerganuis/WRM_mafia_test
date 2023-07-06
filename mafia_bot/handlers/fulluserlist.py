import telegram
from telegram import Update, InputMediaPhoto
from telegram.ext import (
    ContextTypes
)

from mafia_bot import config
from mafia_bot.handlers.response import send_response, send_response_photo
from mafia_bot.handlers.keyboards import (
    get_full_userlist_keyboard
)
from mafia_bot.templates import render_template
from mafia_bot.services.user import (
    validate_user,
    AccessLevel,
    get_userlist
)


@validate_user(AccessLevel.ADMIN)
async def full_userlist(update: Update, context: ContextTypes.DEFAULT_TYPE, access_level: AccessLevel):
    pages_with_users = list(await get_userlist())
    if not update.message:
        return
    await send_response_photo(
        update,
        context,
        render_template("full_userlist.j2"),
        get_full_userlist_keyboard(
            pages_with_users[0],
            callback_prefix={
                "userlist": config.FULL_USERLIST_CALLBACK_PATTERN,
                "user_profile": f"{config.VIEW_USER_PROFILE_CALLBACK_PATTERN}{config.FULL_USERLIST_CALLBACK_PATTERN}0_0"
            },
            page_count=len(pages_with_users),
            current_page_index=0
        )
    )


async def full_userlist_page_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    pages_with_users = list(await get_userlist())
    current_page_index = _get_current_page_index(query.data)
    with open(config.BASE_PHOTO, 'rb') as photo:
        await query.edit_message_media(
            InputMediaPhoto(
                media=photo,
                caption=render_template("full_userlist.j2"),
                parse_mode=telegram.constants.ParseMode.HTML,
            ),
            reply_markup=get_full_userlist_keyboard(
                pages_with_users[current_page_index],
                callback_prefix={
                    "userlist": config.FULL_USERLIST_CALLBACK_PATTERN,
                    "user_profile": f"{config.VIEW_USER_PROFILE_CALLBACK_PATTERN}{config.FULL_USERLIST_CALLBACK_PATTERN}0_0"
                },
                page_count=len(pages_with_users),
                current_page_index=current_page_index,
            )
        )


def _get_current_page_index(query_data) -> int:
    pattern_prefix_length = len(config.FULL_USERLIST_CALLBACK_PATTERN)
    return int(query_data[pattern_prefix_length:])
