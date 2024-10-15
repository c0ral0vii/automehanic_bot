from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def create_catalog_keyboard():
    button_single_article = InlineKeyboardButton(text="Запрос одного артикула", callback_data="request_single_article")
    button_multiple_articles = InlineKeyboardButton(text="Запрос нескольких артикулов", callback_data="request_multiple_articles")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [button_single_article],
        [button_multiple_articles]
    ])

    return keyboard