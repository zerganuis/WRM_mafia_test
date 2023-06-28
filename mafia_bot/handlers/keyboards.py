from collections.abc import Iterable

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from mafia_bot.services.events import Event

def get_page_keyboard(
    current_page_index: int, page_count: int, callback_prefix: str) -> InlineKeyboardMarkup:
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

def get_events_keyboard(
        events_on_page: Iterable[Event],
        events_callback_prefix: str,
        event_callback_prefix: str,
        page_count: int
    ) -> InlineKeyboardMarkup:
    keyboard = []
    for event in events_on_page:
        keyboard.append(
            [InlineKeyboardButton(
                event.name,
                callback_data=f"{event_callback_prefix}{event.id}"
            )]
        )
    keyboard.append(
        get_page_keyboard(
            current_page_index=0,
            page_count=page_count,
            callback_prefix=events_callback_prefix,
        ).inline_keyboard[0]
    )
    return InlineKeyboardMarkup(keyboard)

def get_event_keyboard(callback_prefix: str):
    keyboard = [
        [InlineKeyboardButton(
            "Игроки", callback_data=f"{callback_prefix}{0}"
        )],
        [InlineKeyboardButton(
            "Записаться", callback_data=f"{callback_prefix}{1}"
        )]
    ]
    return InlineKeyboardMarkup(keyboard)