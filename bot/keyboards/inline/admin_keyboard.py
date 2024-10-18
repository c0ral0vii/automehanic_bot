from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def create_inline_navigation():
    cancel_button = InlineKeyboardButton(text="Отмена", callback_data="cancel")
    back_button = InlineKeyboardButton(text="Назад", callback_data="back")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [cancel_button, back_button]
    ])

    return keyboard

def create_simple_inline_navigation():
    cancel_button = InlineKeyboardButton(text="Отмена", callback_data="cancel")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [cancel_button]
    ])

    return keyboard