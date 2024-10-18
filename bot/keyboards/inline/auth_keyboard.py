from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def create_inline_navigation_keyboard():
    cancel_button = InlineKeyboardButton(text="Отмена", callback_data="cancel")
    back_button = InlineKeyboardButton(text="Назад", callback_data="back")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [cancel_button, back_button]
    ])

    return keyboard