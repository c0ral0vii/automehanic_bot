from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def create_contact_keyboard():
    button_ask_question = InlineKeyboardButton(text="Задать вопрос", callback_data="ask_question")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [button_ask_question]
    ])

    return keyboard

def create_inline_navigation_keyboard():
    cancel_button = InlineKeyboardButton(text="Отмена", callback_data="cancel")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [cancel_button]
    ])

    return keyboard