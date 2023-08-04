import os
from pathlib import Path
import json

from dotenv import load_dotenv

load_dotenv()


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# directories

BASE_DIR = Path(__file__).resolve().parent
SQLITE_DB_FILE = BASE_DIR / 'db.sqlite3'
TEMPLATES_DIR = BASE_DIR / 'templates'
PHOTOS_DIR = BASE_DIR / 'photos'
BASE_PHOTO = PHOTOS_DIR / "base.jpg"
USERS_PHOTOS_DIR = PHOTOS_DIR / "users"
BASE_USER_PHOTO = USERS_PHOTOS_DIR / "base_user_profile_photo.jpg"
INFO_PHOTOS_DIR = PHOTOS_DIR / "info"
ROLE_PHOTOS_DIR = PHOTOS_DIR / "roles"
EVENT_PHOTOS_DIR = PHOTOS_DIR / "events"
EVENT_PICTURES = [EVENT_PHOTOS_DIR / f"{i}.jpg" for i in range(9)]
INFO_PICTURES = [INFO_PHOTOS_DIR / f"{i}.jpg" for i in range(7)]

# callback patterns

EVENTLIST_CALLBACK_PATTERN = "eventlist_"
EVENT_PROFILE_CALLBACK_PATTERN = "eventprofile_"
USERLIST_CALLBACK_PATTERN = "userlist_"
FULL_USERLIST_CALLBACK_PATTERN = "fulluserlist_"
VIEW_USER_PROFILE_CALLBACK_PATTERN = "userprofile_"
OWN_USER_PROFILE_CALLBACK_PATTERN = "ownuserprofile_"
TOP_MENU_CALLBACK_PATTERN = "top_"
TOP_SUBMENU_CALLBACK_PATTERN = "topsubmenu_"
RULES_CALLBACK_PATTERN = "rules_"
RULE_CALLBACK_PATTERN = "rule_"
ROLE_CALLBACK_PATTERN = "role_"
EDIT_USER_PROFILE_CALLBACK_PATTERN = "edituser_"
EDIT_EVENT_PROFILE_CALLBACK_PATTERN = "editevent_"
EVENT_SIGN_UP_CALLBACK_PATTERN = "signup_"
GRADE_CALLBACK_PATTERN = "grade_"
GRADE_REQEST_CALLBACK_PATTERN = "gradereqest_"
ISWINNER_CALLBACK_PATTERN = "iswinner_"
CHANGE_ACCESS_CALLBACK_PATTERN = "changeaccess_"

# other constants

EVENTLIST_PAGE_LENGTH = 2
USERLIST_PAGE_LENGTH = 15
TOP_PAGE_LENGTH = 10
DATETIME_FORMAT = rf"%d.%m.%Y %H:%M"
RULES_JSON = json.load(open(BASE_DIR / "rules.json", encoding='UTF-8'))
ALL_ROLES = RULES_JSON['all_roles']
ALL_RULES = RULES_JSON['all_rules']
RULES_TEMPLATES_DIR = 'rules/'
