from telegram import InlineKeyboardButton, InlineKeyboardMarkup


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
