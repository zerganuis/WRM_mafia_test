import time
from datetime import timedelta, datetime

import telegram
from telegram import Update
from telegram.ext import ContextTypes

from mafia_bot.services.eventlist import get_eventlist
from mafia_bot.services.userlist import get_event_participants
from mafia_bot.templates import render_template


def get_event_type_name(event_type):
    match event_type:
        case "mafia":
            return "Мафия"
        case "flow":
            return "CashFlow"
        case "bunker":
            return "Бункер"
        case _:
            raise ValueError( f"Invalid event type: {event_type}" )


async def event_notification(context: ContextTypes.DEFAULT_TYPE):
    period = timedelta(0)
    args = {
        "disable_web_page_preview": True,
        "parse_mode": telegram.constants.ParseMode.HTML,
    }
    actual_events = await get_eventlist(period)
    for page in actual_events:
        for event in page:
            if event.datetime.date() > datetime.now().date() + timedelta(1):
                continue
            args["text"] = render_template(
                "event_notification.j2",
                {
                    "event": event,
                    "event_type": get_event_type_name(event.event_type),
                    "event_date": event.datetime.date().strftime(rf"%d.%m"),
                    "event_time": event.datetime.time().strftime(rf"%H:%M")
                }
            )
            userlist = await get_event_participants(event.id)
            for userpage in userlist:
                for user in userpage:
                    args["chat_id"] = user.id
                    await context.bot.send_message(**args)
