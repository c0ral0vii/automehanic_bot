from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def create_catalog_keyboard():
    button_single_article = InlineKeyboardButton(text="Запрос одного артикула", callback_data="request_single_article")
    button_multiple_articles = InlineKeyboardButton(text="Запрос нескольких артикулов", callback_data="request_multiple_articles")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [button_single_article],
        [button_multiple_articles]
    ])

    return keyboard

def create_product_keyboard():
    order_button = InlineKeyboardButton(text="Оформить заказ", callback_data="order_request")
    back_button = InlineKeyboardButton(text="Назад", callback_data="back")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [order_button, back_button]
    ])

    return keyboard

def create_product_only_order():
    order_button = InlineKeyboardButton(text="Оформить заказ", callback_data="order_request")
    back_button = InlineKeyboardButton(text="Назад", callback_data="back")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [order_button, back_button]
    ])

    return keyboard

def create_more_info_keyboard():
    order_button = InlineKeyboardButton(text="Подробнее", callback_data="view_details")
    back_button = InlineKeyboardButton(text="Назад", callback_data="back")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [order_button],
        [back_button]
    ])

    return keyboard

def create_simple_inline_navigation():
    cancel_button = InlineKeyboardButton(text="Отмена", callback_data="cancel")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [cancel_button]
    ])

    return keyboard

def create_inline_navigation():
    cancel_button = InlineKeyboardButton(text="Отмена", callback_data="cancel")
    back_button = InlineKeyboardButton(text="Назад", callback_data="back")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [cancel_button, back_button]
    ])

    return keyboard
