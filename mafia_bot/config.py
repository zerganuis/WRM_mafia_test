import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

BASE_DIR = Path(__file__).resolve().parent
SQLITE_DB_FILE = BASE_DIR.joinpath('db.sqlite3')
TEMPLATES_DIR = BASE_DIR.joinpath('templates')
PHOTOS_DIR = BASE_DIR.joinpath('photos')
BASE_PHOTO = PHOTOS_DIR.joinpath(f"base.jpg")
EVENT_PICTURES = [
    PHOTOS_DIR.joinpath("event_1"),
    PHOTOS_DIR.joinpath("event_2"),
    PHOTOS_DIR.joinpath("event_3"),
]

DATETIME_FORMAT = rf"%d.%m.%Y %H:%M"

EVENTLIST_CALLBACK_PATTERN = "eventlist_"
EVENT_PROFILE_CALLBACK_PATTERN = "eventprofile_"
USERLIST_CALLBACK_PATTERN = "userlist_"
FULL_USERLIST_CALLBACK_PATTERN = "fulluserlist_"
VIEW_USER_PROFILE_CALLBACK_PATTERN = "userprofile_"
OWN_USER_PROFILE_CALLBACK_PATTERN = "ownuserprofile_"
TOP_MENU_CALLBACK_PATTERN = "top_"
TOP_SUBMENU_CALLBACK_PATTERN = "topsubmenu_"
RULES_CALLBACK_PATTERN = "rules_"
RULETYPE_CALLBACK_PATTERN = "ruletype_"
ROLE_CALLBACK_PATTERN = "role_"
EDIT_USER_PROFILE_CALLBACK_PATTERN = "edituser_"
EDIT_EVENT_PROFILE_CALLBACK_PATTERN = "editevent_"
EVENT_SIGN_UP_CALLBACK_PATTERN = "signup_"
GRADE_CALLBACK_PATTERN = "grade_"
GRADE_REQEST_CALLBACK_PATTERN = "gradereqest_"
ISWINNER_CALLBACK_PATTERN = "iswinner_"
CHANGE_ACCESS_CALLBACK_PATTERN = "changeaccess_"


EVENTLIST_PAGE_LENGTH = 2
USERLIST_PAGE_LENGTH = 15
TOP_PAGE_LENGTH = 10
