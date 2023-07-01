import datetime

import telegram
from telegram import Update
from telegram.ext import ContextTypes

from mafia_bot import config
from mafia_bot.handlers.response import send_response
from mafia_bot.handlers.keyboards import get_rules_keyboard, get_role_keyboard, get_ruletype_keyboard
from mafia_bot.templates import render_template

template_prefix = "rules/"

_all_roletypes = {
    "classic": "Классическая (спортивная) мафия",
    "city": "Городская мафия"
}

_all_roles = {
    "classic": {
        "mafia": "Мафия",
        "peaceful": "Мирный житель",
        "sheriff": "Шериф",
        "don": "Дон"
    },
    "city": {
        "mafia": "Мафозник",
        "peaceful": "Мирный",
        "sheriff": "Комиссар",
        "don": "Дон-дон"
    }
}


async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    await send_response(
        update,
        context,
        render_template(
            f"{template_prefix}rules_menu.j2"
        ),
        get_rules_keyboard(
            _all_roletypes,
            f"{config.RULETYPE_CALLBACK_PATTERN}"
        )
    )


async def rules_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    await query.edit_message_text(
        text=render_template(
            f"{template_prefix}rules_menu.j2"
        ),
        reply_markup=get_rules_keyboard(
            _all_roletypes,
            f"{config.RULETYPE_CALLBACK_PATTERN}"
        ),
        parse_mode=telegram.constants.ParseMode.HTML,
    )


async def ruletype_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    ruletype = _get_ruletype(query.data)
    await query.edit_message_text(
        text=render_template(
            f"{template_prefix}{ruletype}_rules.j2"
        ),
        reply_markup=get_ruletype_keyboard(
            _all_roles[ruletype],
            {
                "role": f"{config.ROLE_CALLBACK_PATTERN}{query.data}_",
                "back": f"{config.RULES_CALLBACK_PATTERN}0"
            }
        ),
        parse_mode=telegram.constants.ParseMode.HTML,
    )


async def role_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    role = _get_role(query.data)
    prev_callback = _get_prev_callback(query.data, config.ROLE_CALLBACK_PATTERN)
    await query.edit_message_text(
        text=render_template(
            f"{template_prefix}{role}.j2"
        ),
        reply_markup=get_role_keyboard(
            f"{prev_callback}"
        ),
        parse_mode=telegram.constants.ParseMode.HTML,
    )


def _get_role(query_data: str) -> str:
    pattern_prefix_length = query_data.rfind("_") + 1
    role = query_data[pattern_prefix_length:]
    return role


def _get_ruletype(query_data) -> str:
    pattern_prefix_length = len(config.RULETYPE_CALLBACK_PATTERN)
    period = query_data[pattern_prefix_length:]
    return period


def _get_prev_callback(query_data, current_callback) -> str:
    pattern_prefix_length = len(current_callback)
    pattern_postfix_length = query_data.rfind("_")
    return query_data[pattern_prefix_length:pattern_postfix_length]
