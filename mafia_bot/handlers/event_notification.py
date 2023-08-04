import time
from datetime import timedelta

import telegram
from telegram import Update
from telegram.ext import ContextTypes

from mafia_bot.services.eventlist import get_eventlist
from mafia_bot.services.userlist import get_event_participants

from pprint import pprint

async def event_notification(context: ContextTypes.DEFAULT_TYPE):
    period = timedelta(0)
    args = {
        "disable_web_page_preview": True,
        "parse_mode": telegram.constants.ParseMode.HTML,
    }
    actual_events = await get_eventlist(period)
    pprint(actual_events)
    print()
    for page in actual_events:
        for event in page:
            args["text"] = event.name
            userlist = await get_event_participants(event.id)
            pprint(event.name)
            pprint(userlist)
            for userpage in userlist:
                for user in userpage:
                    args["chat_id"] = user.id
                    pprint(user.id)
                    await context.bot.send_message(**args)
