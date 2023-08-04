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
BASE_EVENT_PHOTO = EVENT_PHOTOS_DIR / "base_event.jpg"

# callback patterns

EVENTS_CALLBACK_PATTERN = "e-list_"
ALLEVENTS_CALLBACK_PATTERN = "alle-list_"
EVENT_PROFILE_CALLBACK_PATTERN = "e-prof_"
USER_PROFILE_CALLBACK_PATTERN = "u-prof_"
EVENT_PARTICIPANTS_CALLBACK_PATTERN = "e-parts_"
TOP_MENU_CALLBACK_PATTERN = "top_"
TOP_SUBMENU_CALLBACK_PATTERN = "topsubmenu_"
RULELIST_CALLBACK_PATTERN = "rulelist_"
RULETYPE_CALLBACK_PATTERN = "ruletype_"
ROLE_CALLBACK_PATTERN = "role_"
EDIT_USER_PROFILE_CALLBACK_PATTERN = "edituser_"
EDIT_USER_PARAMETER_CALLBACK_PATTERN = "edituserparameter_"
EDIT_EVENT_PROFILE_CALLBACK_PATTERN = "editevent_"
EDIT_EVENT_PARAMETER_CALLBACK_PATTERN = "editeventparameter_"
EVENT_SIGN_UP_CALLBACK_PATTERN = "signup_"
GRADE_CALLBACK_PATTERN = "grade_"
CHANGE_ACCESS_CALLBACK_PATTERN = "changeaccess_"
GRADE_REQEST_CALLBACK_PATTERN = "gradereqest_"
USERLIST_CALLBACK_PATTERN = "userlist_"
SUBMIT_PHOTO_CALLBACK_PATTERN = "submit_"
EVENT_PHOTOS_CALLBACK_PATTERN = "e-photos_"
DELETE_PHOTO_CALLBACK_PATTERN = "deletephoto_"
SUBMIT_DELETE_PHOTO_CALLBACK_PATTERN = "submitdeletephoto_"
ADD_PHOTO_CALLBACK_PATTERN = "addphoto_"
REG_EVENT_TYPE_CALLBACK_PATTERN = "rege-type_"
EDIT_EVENT_TYPE_CALLBACK_PATTERN = "edite-type_"

### пока не используется, заготовка под заказ ведущего
HOST_PROFILE_CALLBACK_PATTERN = "hostprofile_"

# other constants

BASE_PAGE_LENGTH = 10
EVENTLIST_PAGE_LENGTH = 4
USERLIST_PAGE_LENGTH = 10
TOP_PAGE_LENGTH = 10
DATETIME_FORMAT = rf"%d.%m.%Y %H:%M"
RULES_JSON = json.load(open(BASE_DIR / "rules.json", encoding='UTF-8'))
ALL_ROLES = RULES_JSON['all_roles']
ALL_RULES = RULES_JSON['all_rules']
TOP_PERIODS_JSON = json.load(open(BASE_DIR / "top_periods.json", encoding='UTF-8'))
RULES_TEMPLATES_DIR = 'rules/'
REG_TEMPLATES_DIR = 'reg/'
REGEVENT_TEMPLATES_DIR = 'regevent/'
