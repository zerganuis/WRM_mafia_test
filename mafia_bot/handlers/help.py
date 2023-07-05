from telegram import Update
from telegram.ext import ContextTypes

from mafia_bot.handlers.response import send_response
from mafia_bot.templates import render_template
from mafia_bot.services.user import validate_user, AccessLevel

@validate_user(AccessLevel.WALKER)
async def help_(update: Update, context: ContextTypes.DEFAULT_TYPE, access_level: AccessLevel):
    if access_level == AccessLevel.ADMIN:
        template = "help_admin.j2"
    elif access_level == AccessLevel.USER:
        template = "help_user.j2"
    else:
        template = "help_walker.j2"
    await send_response(update, context, response=render_template(template))
