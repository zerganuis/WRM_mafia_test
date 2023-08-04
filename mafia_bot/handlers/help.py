from telegram import Update
from telegram.ext import ContextTypes

from mafia_bot.handlers.response import send_text_response
from mafia_bot.templates import render_template
from mafia_bot.services.user import validate_user, AccessLevel


@validate_user(AccessLevel.WALKER)
async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE, access_level: AccessLevel):
    match access_level:
        case AccessLevel.ADMIN:
            template = "help_admin.j2"
        case AccessLevel.USER:
            template = "help_user.j2"
        case AccessLevel.WALKER:
            template = "help_walker.j2"
        case _:
            raise ValueError(f"Invalid access_level: {access_level}")
    await send_text_response(
        update,
        context,
        response=render_template(template))
