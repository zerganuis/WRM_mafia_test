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


def get_delete_photo_type_keyboard(
        callback_prefix: dict[str, str]
) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(f"{key}", callback_data=f"{value}")]
        for key, value in callback_prefix.items()
    ]
    return InlineKeyboardMarkup(keyboard)


def get_photolist_keyboard(
        current_photo_index: int,
        photo_count: int,
        callback_prefix: dict[str, str]
) -> InlineKeyboardMarkup:
    prev_index = current_photo_index - 1
    if prev_index < 0:
        prev_index = photo_count - 1
    next_index = current_photo_index + 1
    if next_index > photo_count - 1:
        next_index = 0
    keyboard = [[]]
    keyboard[0].append(InlineKeyboardButton(
        "<",
        callback_data=f"{callback_prefix['page']}{prev_index}"
    ))
    if callback_prefix.get("submit", None):
        keyboard[0].append(InlineKeyboardButton(
            f"Выбрать ({current_photo_index + 1}/{photo_count})",
            callback_data=f"{callback_prefix['submit']}"
        ))
    elif callback_prefix.get("delete", None):
        keyboard[0].append(InlineKeyboardButton(
            f"Удалить ({current_photo_index + 1}/{photo_count})",
            callback_data=f"{callback_prefix['delete']}"
        ))
    keyboard[0].append(InlineKeyboardButton(
        ">",
        callback_data=f"{callback_prefix['page']}{next_index}",
    ))
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
            f"Игроки ({callback_prefix['participants']['count']})",
            callback_data=f"{callback_prefix['participants']['callback']}"
        )]
    ]
    if callback_prefix.get("sign_up", None):
        if is_signed_up:
            sign_up_button_name = "Отменить запись"
        else:
            sign_up_button_name = "Записаться"
        keyboard.append(
            [InlineKeyboardButton(
                sign_up_button_name, callback_data=f"{callback_prefix['sign_up']}"
            )]
        )
    if "edit" in callback_prefix.keys():
        keyboard.append(
            [InlineKeyboardButton(
                "Редактировать", callback_data=f"{callback_prefix['edit']}"
            )]
        )
    keyboard.append(
        [InlineKeyboardButton(
            "< Назад", callback_data=f"{callback_prefix['back']}"
        )]
    )
    return InlineKeyboardMarkup(keyboard)


def get_user_profile_keyboard(callback_prefix: dict[str, str], user_access_level_id: int):
    keyboard = []
    if callback_prefix.get("edit_profile", None):
        keyboard.append([InlineKeyboardButton(
            "Редактировать", callback_data=f"{callback_prefix['edit_profile']}"
        )])
    if callback_prefix.get("grade", None):
        keyboard.append([InlineKeyboardButton(
            "Выставить баллы", callback_data=f"{callback_prefix['grade']}"
        )])
    if callback_prefix.get("change_access", None):
        if user_access_level_id < 2:
            button_name = "/\\ Админ /\\"
        else:
            button_name = "\\/ Пользователь \\/"
        keyboard.append([InlineKeyboardButton(
            button_name, callback_data=f"{callback_prefix['change_access']}"
        )])
    if callback_prefix.get("back", None):
        keyboard.append([InlineKeyboardButton(
                "< Назад", callback_data=f"{callback_prefix['back']}"
        )])
    return InlineKeyboardMarkup(keyboard)


def get_edit_user_profile_keyboard(
        edit_parameters: dict[str, str],
        user_id: int,
        callback_prefix: dict[str, str]
) -> InlineKeyboardMarkup:
    keyboard = []
    i = True
    pair = []
    for key, value in edit_parameters.items():
        pair.append(InlineKeyboardButton(
            value,
            callback_data=f"{callback_prefix['prefix']}{key}_{user_id}"
        ))
        i = not i
        if i:
            keyboard.append(pair)
            pair = []
    if pair:
        keyboard.append(pair)
    keyboard.append([
        InlineKeyboardButton(
            "< Назад",
            callback_data=f"{callback_prefix['back']}")
    ])
    return InlineKeyboardMarkup(keyboard)


def get_edit_event_profile_keyboard(
        edit_parameters: dict[str, str],
        event_id: int,
        callback_prefix: dict[str, str]
) -> InlineKeyboardMarkup:
    keyboard = []
    i = True
    pair = []
    for key, value in edit_parameters.items():
        pair.append(InlineKeyboardButton(
            value,
            callback_data=f"{callback_prefix['prefix']}{key}_{event_id}")
        )
        i = not i
        if i:
            keyboard.append(pair)
            pair = []
    if pair:
        keyboard.append(pair)
    keyboard.append([
        InlineKeyboardButton(
            "< Назад",
            callback_data=f"{callback_prefix['back']}")
    ])
    return InlineKeyboardMarkup(keyboard)


def get_view_user_profile_keyboard(callback_prefix: dict[str, str]):
    keyboard = []
    if "grade" in callback_prefix.keys():
        if (
            callback_prefix['grade'].find(config.TOP_SUBMENU_CALLBACK_PATTERN) == -1 and
            callback_prefix['grade'].find(config.USERLIST_CALLBACK_PATTERN) == -1
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
            "Выставить суммарные баллы", callback_data=f"{callback_prefix['score']}"
        )],
        [InlineKeyboardButton(
            "Выставить количество игр", callback_data=f"{callback_prefix['game_count']}"
        )],
        [InlineKeyboardButton(
            "Выставить количество побед", callback_data=f"{callback_prefix['win_count']}"
        )],
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


def get_back_keyboard(callback_prefix: str):
    keyboard = [
        [InlineKeyboardButton(
            "< Назад", callback_data=f"{callback_prefix}"
        )]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_element_list_keyboard(
        page: Iterable,
        callback_prefix: dict[str, str],
        page_count: int,
        current_page_index: int,
        get_name: callable
) -> InlineKeyboardMarkup:
    keyboard = []
    for element in page:
        keyboard.append(
            [InlineKeyboardButton(
                get_name(element),
                callback_data=f"{callback_prefix['element']}{element.id}"
            )]
        )
    if page_count > 1:
        keyboard.append(
            get_page_keyboard(
                current_page_index=current_page_index,
                page_count=page_count,
                callback_prefix=callback_prefix["element_list"],
            ).inline_keyboard[0]
        )
    if callback_prefix.get('back', None):
        keyboard.append(
            [InlineKeyboardButton(
                "< Назад", callback_data=f"{callback_prefix['back']}"
            )]
        )
    return InlineKeyboardMarkup(keyboard)
