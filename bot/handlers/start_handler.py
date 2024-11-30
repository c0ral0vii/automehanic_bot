from aiogram import Router, types, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from keyboards.reply.main_keyboard import create_main_keyboard
from database.db_config import check_auth
from utils.texts import get_greeting_text

start_router = Router(name="start")


@start_router.message(CommandStart(), StateFilter(None))
async def start_handler(message: types.Message, state: FSMContext) -> None:
    text = get_greeting_text()
    await state.clear()
    keyboard = create_main_keyboard(auth=await check_auth(user_id=message.from_user.id))

    await message.answer(text, reply_markup=keyboard)
