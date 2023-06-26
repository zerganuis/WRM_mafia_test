import logging

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler
)

# import config
# import handlers
# from db import close_db
import message_templates
import _events

from mafia_bot import config, handlers
from mafia_bot.db import close_db

COMMAND_HANDLERS = {
    "start": handlers.start,
    "help": handlers.help_
}

CALLBACK_QUERY_HANDLERS = {
    
}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat = update.effective_chat
    if not effective_chat:
        logger.warning("effective_chat is None in /start")
        return
    await context.bot.send_message(
        chat_id=effective_chat.id,
        text=message_templates.START)

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat = update.effective_chat
    if not effective_chat:
        logger.warning("effective_chat is None in /help")
        return
    await context.bot.send_message(
        chat_id=effective_chat.id,
        text=message_templates.HELP)

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat = update.effective_chat
    if not effective_chat:
        logger.warning("effective_chat is None in /info")
        return
    await context.bot.send_message(
        chat_id=effective_chat.id,
        text=message_templates.INFO)

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

if not config.BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN is not implemented in .env"
    )

def main():
    application = ApplicationBuilder().token(config.BOT_TOKEN).build()

    for command_name, command_haldler in COMMAND_HANDLERS.items():
        application.add_handler(CommandHandler(command_name, command_haldler))

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    
    help_handler = CommandHandler('help', help)
    application.add_handler(help_handler)

    info_handler = CommandHandler('info', info)
    application.add_handler(info_handler)

    events_handler = CommandHandler('events', events)
    application.add_handler(events_handler)

    application.run_polling()


if __name__ == '__main__':
    try:
        main()
    except Exception:
        import traceback
        logger.warning(traceback.format_exc())
    finally:
        close_db()
