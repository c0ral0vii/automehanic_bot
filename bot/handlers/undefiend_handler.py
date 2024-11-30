from aiogram import Router, types
from aiogram.filters import StateFilter

undefiend_handler = Router(name='undefiend')


@undefiend_handler.message(StateFilter(None))
async def default_handler(message: types.Message):
    await message.answer("Выбери что нибудь в меню!")