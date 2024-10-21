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

def create_user_list_keyboard(users, page: int = 1, total_pages: int = 1):
    price_level_texts = {
        'PriceLevel.DEFAULT': 'Розничный',
        'PriceLevel.FIRST': 'Первый',
        'PriceLevel.SECOND': 'Второй',
        'PriceLevel.THIRD': 'Третий',
        'PriceLevel.FOURTH': 'Четвертый',
    }

    user_buttons = [
        [InlineKeyboardButton(text=f"{user.name} {user.surname} {user.user_id} {price_level_texts[str(user.price_level)]}", callback_data=f"user_{user.user_id}")]
        for user in users
    ]

    navigation_buttons = []
    if page > 1:
        navigation_buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"page_{page - 1}"))
    if page < total_pages:
        navigation_buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"page_{page + 1}"))

    cancel_button = InlineKeyboardButton(text="Отмена", callback_data="cancel")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        *user_buttons,
        navigation_buttons,
        [cancel_button]
    ])

    return keyboard
