from collections.abc import Iterable

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from mafia_bot import config
from mafia_bot.services.event import Event
from mafia_bot.services.user import User

def get_page_keyboard(
        current_page_index: int,
        page_count: int,
        callback_prefix: str
) -> InlineKeyboardMarkup:
    prev_index = current_page_index - 1
    if prev_index < 0:
        prev_index = page_count - 1
    next_index = current_page_index + 1
    if next_index > page_count - 1:
        next_index = 0
    keyboard = [
        [
            InlineKeyboardButton(
                "<",
                callback_data=f"{callback_prefix}{prev_index}"
            ),
            InlineKeyboardButton(
                f"{current_page_index + 1}/{page_count}",
                callback_data=" "
            ),
            InlineKeyboardButton(
                ">",
                callback_data=f"{callback_prefix}{next_index}",
            ),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_eventlist_keyboard(
        events_on_page: Iterable[Event],
        callback_prefix: dict[str, str],
        page_count: int,
        current_page_index: int,
) -> InlineKeyboardMarkup:
    keyboard = []
    for event in events_on_page:
        keyboard.append(
            [InlineKeyboardButton(
                event.name,
                callback_data=f"{callback_prefix['event_profile']}{event.id}"
            )]
        )
    keyboard.append(
        get_page_keyboard(
            current_page_index=current_page_index,
            page_count=page_count,
            callback_prefix=callback_prefix["eventlist"],
        ).inline_keyboard[0]
    )
    return InlineKeyboardMarkup(keyboard)

def get_full_userlist_keyboard(
        users_on_page: Iterable[Event],
        callback_prefix: dict[str, str],
        page_count: int,
        current_page_index: int,
) -> InlineKeyboardMarkup:
    keyboard = []
    for user in users_on_page:
        keyboard.append(
            [InlineKeyboardButton(
                f"{user.name} ({user.nickname})",
                callback_data=f"{callback_prefix['user_profile']}{user.id}"
            )]
        )
    keyboard.append(
        get_page_keyboard(
            current_page_index=current_page_index,
            page_count=page_count,
            callback_prefix=callback_prefix["userlist"],
        ).inline_keyboard[0]
    )
    return InlineKeyboardMarkup(keyboard)

def get_event_profile_keyboard(callback_prefix: dict[str, str], is_signed_up: bool):
    keyboard = [
        [InlineKeyboardButton(
            "Игроки", callback_data=f"{callback_prefix['userlist']}"
        )],
        [InlineKeyboardButton(
            "Отменить запись" if is_signed_up else "Записаться", callback_data=f"{callback_prefix['sign_up']}"
        )]
    ]
    if "edit" in callback_prefix.keys():
        keyboard.append(
            [InlineKeyboardButton(
                "Редактировать", callback_data=f"{callback_prefix['edit']}"
            )]
        )
    keyboard.append(
        [InlineKeyboardButton(
            "< Назад", callback_data=f"{callback_prefix['back']}{0}"
        )]
    )
    return InlineKeyboardMarkup(keyboard)


def get_user_profile_keyboard(callback_prefix: str):
    keyboard = [
        [InlineKeyboardButton(
            "Редактировать", callback_data=f"{callback_prefix}"
        )]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_edit_user_profile_keyboard(callback_prefix: dict[str, str]):
    keyboard = [
        [
            InlineKeyboardButton(
                "Имя",
                callback_data=f"{callback_prefix['name']}"),
            InlineKeyboardButton(
                "Никнейм",
                callback_data=f"{callback_prefix['nickname']}")
        ],
        [
            InlineKeyboardButton(
                "Город",
                callback_data=f"{callback_prefix['city']}"),
            InlineKeyboardButton(
                "Фото",
                callback_data=f"{callback_prefix['photo']}")
        ],
        [
            InlineKeyboardButton(
                "< Назад",
                callback_data=f"{callback_prefix['back']}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_edit_event_profile_keyboard(callback_prefix: dict[str, str]):
    keyboard = [
        [
            InlineKeyboardButton(
                "Название",
                callback_data=f"{callback_prefix['name']}"),
            InlineKeyboardButton(
                "Дата и время",
                callback_data=f"{callback_prefix['datetime']}")
        ],
        [
            InlineKeyboardButton(
                "Место",
                callback_data=f"{callback_prefix['place']}"),
            InlineKeyboardButton(
                "Ведущий",
                callback_data=f"{callback_prefix['host']}")
        ],
        [
            InlineKeyboardButton(
                "Стоимость",
                callback_data=f"{callback_prefix['cost']}"),
            InlineKeyboardButton(
                "Описание",
                callback_data=f"{callback_prefix['description']}")
        ],
        [
            InlineKeyboardButton(
                "< Назад",
                callback_data=f"{callback_prefix['back']}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_view_user_profile_keyboard(callback_prefix: dict[str, str]):
    keyboard = []
    if "grade" in callback_prefix.keys():
        if (
            callback_prefix['grade'].find(config.TOP_SUBMENU_CALLBACK_PATTERN) == -1 and
            callback_prefix['grade'].find(config.FULL_USERLIST_CALLBACK_PATTERN) == -1
        ):
            keyboard = [
                [InlineKeyboardButton(
                    "Выставить баллы", callback_data=f"{callback_prefix['grade']}"
                )]
            ]
    if "access_admin" in callback_prefix.keys():
        keyboard.append(
            [
                InlineKeyboardButton(
                    "/\\ Админ /\\", callback_data=f"{callback_prefix['access_admin']}"
                ),
                InlineKeyboardButton(
                    "\\/ Пользователь \\/", callback_data=f"{callback_prefix['access_user']}"
                )
            ]
        )
    keyboard.append(
        [InlineKeyboardButton(
            "< Назад", callback_data=f"{callback_prefix['back']}"
        )]
    )
    return InlineKeyboardMarkup(keyboard)


def get_grade_user_keyboard(callback_prefix: dict[str, str]):
    keyboard = [
        [InlineKeyboardButton(
            "Выставить баллы", callback_data=f"{callback_prefix['grade']}"
        )],
        [
            InlineKeyboardButton(
                "Победитель", callback_data=f"{callback_prefix['winner']}"
            ),
            InlineKeyboardButton(
                "Проигравший", callback_data=f"{callback_prefix['loser']}"
            )
        ],
        [InlineKeyboardButton(
            "< Назад", callback_data=f"{callback_prefix['back']}"
        )]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_top_menu_keyboard(
        periods: dict,
        callback_prefix: str
) -> InlineKeyboardMarkup:
    keyboard = []
    for key, value in periods.items():
        keyboard.append(
            [InlineKeyboardButton(
                f"{value}",
                callback_data=f"{callback_prefix}{key}"
            )]
        )
    return InlineKeyboardMarkup(keyboard)


def get_userlist_keyboard(
        users_on_page: Iterable[User],
        callback_prefix: dict[str, str],
        button_name
) -> InlineKeyboardMarkup:
    keyboard = []
    for user in users_on_page:
        keyboard.append(
            [InlineKeyboardButton(
                button_name(user),
                callback_data=f"{callback_prefix['user_profile']}{user.id}"
            )]
        )
    keyboard.append(
        [InlineKeyboardButton(
            "< Назад", callback_data=f"{callback_prefix['back']}"
        )]
    )
    return InlineKeyboardMarkup(keyboard)


def get_rules_keyboard(
        ruletypes: dict,
        callback_prefix: str
) -> InlineKeyboardMarkup:
    keyboard = []
    rolelist = list(ruletypes.items())
    rolelist.reverse()
    for key, value in ruletypes.items():
        keyboard.append(
            [InlineKeyboardButton(
                f"{value}",
                callback_data=f"{callback_prefix}{key}"
            )]
        )
    return InlineKeyboardMarkup(keyboard)


def get_ruletype_keyboard(
        roles: dict,
        callback_prefix: dict[str, str]
) -> InlineKeyboardMarkup:
    keyboard = []
    rolelist = list(roles.items())
    rolelist.reverse()
    i = 0
    triplet = []
    while rolelist:
        key, value = rolelist.pop()
        if i > 1:
            keyboard.append(triplet)
            triplet = []; i = 0
        triplet.append(InlineKeyboardButton(
            f"{value}",
            callback_data=f"{callback_prefix['role']}{key}"
        ))
        i += 1
    keyboard.append(triplet)
    keyboard.append(
        [InlineKeyboardButton(
            "< Назад", callback_data=f"{callback_prefix['back']}"
        )]
    )
    return InlineKeyboardMarkup(keyboard)


def get_role_keyboard(callback_prefix: str):
    keyboard = [
        [InlineKeyboardButton(
            "< Назад", callback_data=f"{callback_prefix}"
        )]
    ]
    return InlineKeyboardMarkup(keyboard)
