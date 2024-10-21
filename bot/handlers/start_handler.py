from aiogram import Router, types, F
from aiogram.filters import CommandStart
from keyboards.reply.main_keyboard import create_main_keyboard
from database.db_config import check_auth
from utils.texts import get_greeting_text

start_router = Router(name="start")


@start_router.message(CommandStart())
async def start_handler(message: types.Message) -> None:
    text = get_greeting_text()

    keyboard = create_main_keyboard(auth=await check_auth(user_id=message.from_user.id))

    await message.answer(text, reply_markup=keyboard)
