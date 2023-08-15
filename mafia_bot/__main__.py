import sys
from pathlib import Path
pathvar = str(Path(__file__).resolve().parent.parent) + '/'
sys.path.append(pathvar)

import time as ttime
import datetime
from datetime import time, timedelta
import logging

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler
)

from mafia_bot import config, handlers
from mafia_bot.db import close_db


COMMAND_HANDLERS = {
    "start": handlers.cmd_start,
    "help": handlers.cmd_help,
    "info": handlers.cmd_info,
    "events": handlers.cmd_events,
    "top": handlers.cmd_top,
    "rules": handlers.cmd_rulelist,
    "profile": handlers.cmd_profile,
    "delete": handlers.cmd_delete,
    "userlist": handlers.cmd_userlist,
    "allevents": handlers.cmd_allevents,
    "deletephoto": handlers.cmd_deletephoto,
    "addphoto": handlers.cmd_addphoto,
}

CALLBACK_QUERY_HANDLERS = {
    rf"^{config.EVENTS_CALLBACK_PATTERN}(.+)$": handlers.eventlist_page_button,
    rf"^{config.ALLEVENTS_CALLBACK_PATTERN}(.+)$": handlers.alleventlist_page_button,
    rf"^{config.EVENT_PROFILE_CALLBACK_PATTERN}(.+)$": handlers.event_profile_button,
    rf"^{config.USER_PROFILE_CALLBACK_PATTERN}(.+)$": handlers.user_profile_button,
    rf"^{config.EVENT_PARTICIPANTS_CALLBACK_PATTERN}(.+)$": handlers.event_participants_button,
    rf"^{config.TOP_MENU_CALLBACK_PATTERN}(.+)$": handlers.top_menu_button,
    rf"^{config.TOP_SUBMENU_CALLBACK_PATTERN}(.+)$": handlers.top_submenu_button,
    rf"^{config.RULELIST_CALLBACK_PATTERN}(.+)$": handlers.rulelist_button,
    rf"^{config.RULETYPE_CALLBACK_PATTERN}(.+)$": handlers.ruletype_button,
    rf"^{config.ROLE_CALLBACK_PATTERN}(.+)$": handlers.role_button,
    rf"^{config.EDIT_USER_PROFILE_CALLBACK_PATTERN}(.+)$": handlers.edit_user_profile_button,
    rf"^{config.EDIT_EVENT_PROFILE_CALLBACK_PATTERN}(.+)$": handlers.edit_event_profile_button,
    rf"^{config.EVENT_SIGN_UP_CALLBACK_PATTERN}(.+)$": handlers.sign_up_button,
    rf"^{config.GRADE_CALLBACK_PATTERN}(.+)$": handlers.grade_user_button,
    rf"^{config.CHANGE_ACCESS_CALLBACK_PATTERN}(.+)$": handlers.change_access_button,
    rf"^{config.USERLIST_CALLBACK_PATTERN}(.+)$": handlers.userlist_page_button,
    rf"^{config.EVENT_PHOTOS_CALLBACK_PATTERN}(.+)$": handlers.edit_event_photo_button,
    rf"^{config.DELETE_PHOTO_CALLBACK_PATTERN}(.+)$": handlers.delete_photo_button,
    rf"^{config.SUBMIT_DELETE_PHOTO_CALLBACK_PATTERN}(.+)$": handlers.submit_delete_photo_button,
    rf"^{config.GAMETYPE_CALLBACK_PATTERN}(.+)$": handlers.gamelist_button,
}

CONVERSATION_HANDLERS = [
    handlers.get_registration_conversation(),
    handlers.get_regevent_conversation(),
    handlers.get_edit_user_conversation(),
    handlers.get_edit_event_conversation(),
    handlers.get_edit_user_score_conversation(),
    handlers.add_event_photo_conversation()
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
    # soon = (datetime.datetime.now() + timedelta(seconds=10) - timedelta(hours=3)).time()
    # soon1 = (datetime.datetime.now() + timedelta(seconds=25) - timedelta(hours=3)).time()

    application.job_queue.run_daily(handlers.event_notification, time=time(18, 0)) # 21:00 по нашему
    application.job_queue.run_daily(handlers.birthday_notification, time=time(7, 0)) # 10:00 по нашему

    # application.job_queue.run_daily(handlers.event_notification, time=soon) # 21:00 по нашему
    # application.job_queue.run_daily(handlers.birthday_notification, time=soon1) # 10:00 по нашему

    application.run_polling()

if __name__ == '__main__':
    try:
        main()
    except Exception:
        import traceback
        logger.warning(traceback.format_exc())
    finally:
        close_db()
