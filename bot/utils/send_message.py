from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup

async def notify_user(bot: Bot, user_id: int, message: str):
    await bot.send_message(user_id, message)

async def notify_user_upd(bot: Bot, user_id: int, message: str, reply_markup: InlineKeyboardMarkup):
    await bot.send_message(user_id, message, reply_markup=reply_markup)
