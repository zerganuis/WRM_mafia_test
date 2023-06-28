import sys
from pathlib import Path
pathvar = str(Path(__file__).resolve().parent.parent) + '\\'
sys.path.append(pathvar)

import logging

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler
)

import _events

from mafia_bot import config, handlers
from mafia_bot.db import close_db

COMMAND_HANDLERS = {
    "start": handlers.start,
    "help": handlers.help_,
    "info": handlers.info,
    "events": handlers.events
}

CALLBACK_QUERY_HANDLERS = {
    rf"^{config.EVENTS_CALLBACK_PATTERN}(\d+)$": handlers.all_events_button,
    rf"^{config.EVENT_CALLBACK_PATTERN}(\d+)$": handlers.all_events_button
}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat = update.effective_chat
    if not effective_chat:
        logger.warning("effective_chat is None in /events")
        return
    eventlist = await _events.get_all_events()
    response = "\n".join(f"{event.name}, {event.members}" for event in eventlist)
    await context.bot.send_message(
        chat_id=effective_chat.id,
        text=response)

if not config.TELEGRAM_BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN is not implemented in .env"
    )

def main():
    application = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).build()

    for command_name, command_haldler in COMMAND_HANDLERS.items():
        application.add_handler(CommandHandler(command_name, command_haldler))

    for pattern, handler in CALLBACK_QUERY_HANDLERS.items():
        application.add_handler(CallbackQueryHandler(handler, pattern=pattern))

    application.run_polling()


if __name__ == '__main__':
    try:
        main()
    except Exception:
        import traceback
        logger.warning(traceback.format_exc())
    finally:
        close_db()
