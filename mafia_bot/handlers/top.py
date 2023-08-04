from datetime import timedelta

import telegram
from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes

from mafia_bot import config
from mafia_bot.handlers.response import send_photos_response
from mafia_bot.handlers.keyboards import get_top_menu_keyboard, get_element_list_keyboard
from mafia_bot.templates import render_template
from mafia_bot.services.user import validate_user, AccessLevel
from mafia_bot.handlers.menu import get_id
from mafia_bot.services.userlist import get_userlist

@validate_user(AccessLevel.USER)
async def cmd_top(update: Update, context: ContextTypes.DEFAULT_TYPE, access_level):
    if not update.message:
        return
    await send_photos_response(
        update,
        context,
        render_template(
            "top_menu.j2"
        ),
        get_top_menu_keyboard(
            config.TOP_PERIODS_JSON,
            f"{config.TOP_SUBMENU_CALLBACK_PATTERN}"
        )
    )


async def top_menu_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    await query.edit_message_caption(
        caption=render_template(
            "top_menu.j2"
        ),
        reply_markup=get_top_menu_keyboard(
            config.TOP_PERIODS_JSON,
            f"{config.TOP_SUBMENU_CALLBACK_PATTERN}"
        ),
        parse_mode=telegram.constants.ParseMode.HTML,
    )


async def top_submenu_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    period = get_id(query.data)
    period_timedelta = _get_timedelta(period)
    userlist = await get_userlist(period_timedelta, config.TOP_PAGE_LENGTH)
    await query.edit_message_media(
        InputMediaPhoto(
            media=open(config.BASE_PHOTO, 'rb'),
            caption=render_template(
                "top_submenu.j2",
                {"period": config.TOP_PERIODS_JSON[str(period)].lower()}
            ),
            parse_mode=telegram.constants.ParseMode.HTML,
        ),
        reply_markup=get_element_list_keyboard(
            page=userlist[0],
            callback_prefix={
                "element_list": config.TOP_SUBMENU_CALLBACK_PATTERN,
                "element": f"{config.USER_PROFILE_CALLBACK_PATTERN}{query.data}_",
                "back": f"{config.TOP_MENU_CALLBACK_PATTERN}0"
            },
            page_count=len(userlist),
            current_page_index=0,
            get_name=lambda user: f"{user.name} ({user.total_score})"
        )
    )


def _get_timedelta(period: int | str) -> timedelta:
    if int(period) > 0:
        return timedelta(days=int(period))
    return None
