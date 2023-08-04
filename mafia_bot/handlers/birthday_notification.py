from datetime import timedelta, datetime

import telegram
from telegram import Update
from telegram.ext import ContextTypes

from mafia_bot.services.userlist import get_userlist
from mafia_bot.services.user import get_constant_admin_list, AccessLevel


async def birthday_notification(context: ContextTypes.DEFAULT_TYPE):
    args = {
        "disable_web_page_preview": True,
        "parse_mode": telegram.constants.ParseMode.HTML,
    }
    userlist = await get_userlist()
    adminlist = await get_constant_admin_list()
    # getting admins
    for userpage in userlist:
        for user in userpage:
            if user.access_level == AccessLevel.ADMIN and not user.id in adminlist:
                adminlist.append(user.id)
    # sending notification
    now = datetime.now()
    for userpage in userlist:
        for user in userpage:
            if user.birthday and \
                    now < \
                    datetime(now.year, user.birthday.month, user.birthday.day) <= \
                    now + timedelta(days=7):
                args["text"] = f"{user.name} has birthday soon"
                for admin in adminlist:
                    args["chat_id"] = admin
                    await context.bot.send_message(**args)
