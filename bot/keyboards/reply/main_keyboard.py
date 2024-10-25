from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def create_main_keyboard(auth: bool = False):
    if auth:
        button_auth = KeyboardButton(text='👨‍🦱Мой профиль')
    else:
        button_auth = KeyboardButton(text="🔐 Авторизоваться")
    button_catalog = KeyboardButton(text="📦 Каталог")
    button_presentations = KeyboardButton(text="📑 Презентации по продукту")
    button_contact = KeyboardButton(text="📞 Связаться с нами")

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [button_catalog],
            [button_presentations],
            [button_contact, button_auth],
        ],
        resize_keyboard=True
    )

    return keyboard