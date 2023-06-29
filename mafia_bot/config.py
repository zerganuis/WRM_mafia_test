import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

BASE_DIR = Path(__file__).resolve().parent
SQLITE_DB_FILE = BASE_DIR.joinpath('db.sqlite3')
TEMPLATES_DIR = BASE_DIR.joinpath('templates')

DATE_FORMAT = "%d.%m.%Y"

EVENTLIST_CALLBACK_PATTERN = "eventlist_"
EVENT_CALLBACK_PATTERN = "event_"
EVENT_PROFILE_CALLBACK_PATTERN = "eventprofile_"

EVENTLIST_PAGE_LENGTH = 2
