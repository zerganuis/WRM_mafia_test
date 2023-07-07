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

from mafia_bot import config, handlers
from mafia_bot.db import close_db

COMMAND_HANDLERS = {
    "start": handlers.start,
    "help": handlers.help_,
    "info": handlers.info,
    "events": handlers.eventlist,
    "top": handlers.top,
    "rules": handlers.rules,
    "profile": handlers.profile,
    "delete": handlers.delete,
    "userlist": handlers.full_userlist
}

CALLBACK_QUERY_HANDLERS = {
    rf"^{config.EVENTLIST_CALLBACK_PATTERN}(.+)$": handlers.eventlist_page_button,
    rf"^{config.EVENT_PROFILE_CALLBACK_PATTERN}(.+)$": handlers.event_profile_button,
    rf"^{config.VIEW_USER_PROFILE_CALLBACK_PATTERN}(.+)$": handlers.view_user_profile_button,
    rf"^{config.USERLIST_CALLBACK_PATTERN}(.+)$": handlers.userlist_button,
    rf"^{config.FULL_USERLIST_CALLBACK_PATTERN}(.+)$": handlers.full_userlist_page_button,
    rf"^{config.TOP_MENU_CALLBACK_PATTERN}(.+)$": handlers.top_menu_button,
    rf"^{config.TOP_SUBMENU_CALLBACK_PATTERN}(.+)$": handlers.top_submenu_button,
    rf"^{config.RULES_CALLBACK_PATTERN}(.+)$": handlers.rules_button,
    rf"^{config.RULETYPE_CALLBACK_PATTERN}(.+)$": handlers.ruletype_button,
    rf"^{config.ROLE_CALLBACK_PATTERN}(.+)$": handlers.role_button,
    rf"^{config.EDIT_USER_PROFILE_CALLBACK_PATTERN}(.+)$": handlers.edit_user_profile_button,
    rf"^{config.OWN_USER_PROFILE_CALLBACK_PATTERN}(.+)$": handlers.user_profile_button,
    rf"^{config.EDIT_EVENT_PROFILE_CALLBACK_PATTERN}(.+)$": handlers.edit_event_profile_button,
    rf"^{config.EVENT_SIGN_UP_CALLBACK_PATTERN}(.+)$": handlers.sign_up_button,
    rf"^{config.GRADE_CALLBACK_PATTERN}(.+)$": handlers.grade_user_button,
    rf"^{config.ISWINNER_CALLBACK_PATTERN}(.+)$": handlers.is_winner_user_button,
    rf"^{config.CHANGE_ACCESS_CALLBACK_PATTERN}(.+)$": handlers.change_access_button,
}

CONVERSATION_HANDLERS = [
    handlers.get_registration_conversation(),
    handlers.get_edit_user_conversation(),
    handlers.get_edit_event_conversation(),
    handlers.get_regevent_conversation(),
    handlers.get_edit_user_score_conversation()
]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

if not config.TELEGRAM_BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN is not implemented in .env"
    )

def main():
    application = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).build()

    for handler in CONVERSATION_HANDLERS:
        application.add_handler(handler)

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
