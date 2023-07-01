import datetime

import telegram
from telegram import Update
from telegram.ext import ContextTypes

from mafia_bot import config
from mafia_bot.handlers.response import send_response
from mafia_bot.handlers.keyboards import get_rules_menu_keyboard, get_rules_submenu_keyboard
from mafia_bot.templates import render_template
from mafia_bot.services.user import get_top_users

template_prefix = "rules/"

_all_roles = {
    "mafia": "Мафия",
    "peaceful": "Мирный житель",
    "sheriff": "Шериф",
    "don": "Дон"
}

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    await send_response(
        update,
        context,
        render_template(
            f"{template_prefix}main_rules.j2"
        ),
        get_rules_menu_keyboard(
            _all_roles,
            f"{config.RULES_SUBMENU_CALLBACK_PATTERN}"
        )
    )


async def rules_menu_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    await query.edit_message_text(
        text=render_template(
            f"{template_prefix}main_rules.j2"
        ),
        reply_markup=get_rules_menu_keyboard(
            _all_roles,
            f"{config.RULES_SUBMENU_CALLBACK_PATTERN}"
        ),
        parse_mode=telegram.constants.ParseMode.HTML,
    )


async def rules_submenu_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    role = _get_role(query.data)
    await query.edit_message_text(
        text=render_template(
            f"{template_prefix}{role}.j2"
        ),
        reply_markup=get_rules_submenu_keyboard(
            f"{config.RULES_MENU_CALLBACK_PATTERN}0"
        ),
        parse_mode=telegram.constants.ParseMode.HTML,
    )


def _get_role(query_data) -> str:
    pattern_prefix_length = len(config.RULES_SUBMENU_CALLBACK_PATTERN)
    period = query_data[pattern_prefix_length:]
    return period
