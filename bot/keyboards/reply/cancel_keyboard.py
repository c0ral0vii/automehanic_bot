from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def create_cancel_keyboard():
    button_cancel = KeyboardButton(text="Назад")

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [button_cancel],
        ],
        resize_keyboard=True,
    )

    return keyboard
