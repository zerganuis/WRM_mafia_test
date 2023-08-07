import telegram
from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes

from mafia_bot import config
from mafia_bot.handlers.menu import get_id, get_prev_callback
from mafia_bot.handlers.response import send_photos_response
from mafia_bot.handlers.keyboards import get_rules_keyboard, get_back_keyboard, get_ruletype_keyboard
from mafia_bot.templates import render_template


async def cmd_rulelist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    await send_photos_response(
        update,
        context,
        caption=render_template(
            f"{config.RULES_TEMPLATES_DIR}gamelist_menu.j2"
        ),
        keyboard=get_rules_keyboard(
            config.ALL_GAMETYPES,
            {
                "rule": f"{config.RULELIST_CALLBACK_PATTERN}"
            }
        )
    )


async def gamelist_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    await query.edit_message_caption(
        caption=render_template(
            f"{config.RULES_TEMPLATES_DIR}gamelist_menu.j2"
        ),
        reply_markup=get_rules_keyboard(
            config.ALL_GAMETYPES,
            {
                "rule": f"{config.RULELIST_CALLBACK_PATTERN}"
            }
        ),
        parse_mode=telegram.constants.ParseMode.HTML,
    )


async def rulelist_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    ruletype = get_id(query.data)
    template = f"{config.RULES_TEMPLATES_DIR}rulelist_menu.j2"
    if ruletype in ["cashflow", "bunker"]:
        template = f"{config.RULES_TEMPLATES_DIR}{ruletype}_rules.j2"
    await query.edit_message_caption(
        caption=render_template(template),
        reply_markup=get_rules_keyboard(
            config.ALL_RULES.get(ruletype, {}),
            {
                "rule": f"{config.RULETYPE_CALLBACK_PATTERN}{query.data}_",
                "back": f"{config.GAMETYPE_CALLBACK_PATTERN}{0}"
            }
        ),
        parse_mode=telegram.constants.ParseMode.HTML,
    )


async def ruletype_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    ruletype = get_id(query.data)
    await query.edit_message_media(
        InputMediaPhoto(
            media=open(config.BASE_PHOTO, 'rb'),
            caption=render_template(
                f"{config.RULES_TEMPLATES_DIR}{ruletype}_rules.j2"
            ),
            parse_mode=telegram.constants.ParseMode.HTML,
        ),
        reply_markup=get_ruletype_keyboard(
                config.ALL_ROLES.get(ruletype, {}),
                {
                    "role": f"{config.ROLE_CALLBACK_PATTERN}{query.data}_",
                    "back": f"{config.RULELIST_CALLBACK_PATTERN}mafia"
                }
            )
    )


async def role_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    role = get_id(query.data)
    prev_callback = get_prev_callback(query.data)
    await query.edit_message_media(
        InputMediaPhoto(
            media=open(config.ROLE_PHOTOS_DIR.joinpath(f"{role}.jpg"), 'rb'),
            caption=render_template(
                f"{config.RULES_TEMPLATES_DIR}{role}.j2"
            ),
            parse_mode=telegram.constants.ParseMode.HTML,
        ),
        reply_markup=get_back_keyboard(
            f"{prev_callback}"
        )
    )
