from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def create_admin_navigation():
    button_status = KeyboardButton(text='Админ:')
    button_auth = KeyboardButton(text="🔐 Авторизация")
    button_catalog = KeyboardButton(text="📦 Изменить уровень цен")
    button_contact = KeyboardButton(text="📞 Отправить рассылку")
    button_reload = KeyboardButton(text='🔃Обновить каталог')

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [button_status],
            [button_auth],
            [button_catalog],
            [button_contact, button_reload],
        ],
        resize_keyboard=True
    )

    return keyboard

def create_auth_navigation():
    auth_requests = KeyboardButton(text="Запросы на авторизацию")
    all_users = KeyboardButton(text="Все пользователи")
    all_auth_users = KeyboardButton(text="Все авторизованные пользователи")
    cancel_button = KeyboardButton(text="Отмена")

    keyboard = ReplyKeyboardMarkup(keyboard=[
        [auth_requests],
        [all_users],
        [all_auth_users],
        [cancel_button]
    ],
    resize_keyboard=True
    )

    return keyboard

def create_catalog_navigation():
    change_one_user = KeyboardButton(text="Поменять одному пользователю")
    change_group = KeyboardButton(text="Поменять группе пользователей")
    change_cateogory = KeyboardButton(text="Поменять категории пользователей")
    change_all_users = KeyboardButton(text="Поменять всем пользователям")
    cancel_button = KeyboardButton(text="Отмена")

    keyboard = ReplyKeyboardMarkup(keyboard=[
        [change_one_user, change_group],
        [change_cateogory, change_all_users],
        [cancel_button]
    ],
    resize_keyboard=True
    )

    return keyboard

def create_notification_navigation():
    all_users = KeyboardButton(text="Отправить рассылку всем пользователем")
    specifiс_user = KeyboardButton(text="Отправить рассылку определенному пользователю")
    cancel_button = KeyboardButton(text="Отмена")

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [all_users],
            [specifiс_user],
            [cancel_button]
        ],
        resize_keyboard=True
    )

    return keyboard
