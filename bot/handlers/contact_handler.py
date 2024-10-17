from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from keyboards.inline.contact_keyboard import create_contact_keyboard, create_inline_navigation_keyboard
from utils.texts import get_contact_text
from utils.send_email import send_contact_email

contact_router = Router(name="contact")

class Form(StatesGroup):
    question = State()

@contact_router.message(StateFilter(None), F.text == '📞 Связаться с нами')
async def contact_handler(message: types.Message):
    text = get_contact_text()
    keyboard = create_contact_keyboard()
    await message.answer(text, reply_markup=keyboard)

@contact_router.callback_query(lambda c: c.data == "ask_question")
async def handle_single_article_request(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите ваш вопрос:", reply_markup=create_inline_navigation_keyboard())
    await state.set_state(Form.question)

@contact_router.message(StateFilter(Form.question), F.text)
async def handle_question(message: types.Message, state: FSMContext):
    question = message.text.strip()

    user_id = message.from_user.id
    username = message.from_user.username or "Не указано"

    await send_contact_email(user_id, username, question)

    await message.answer("Спасибо за ваш вопрос! Мы получили ваше сообщение и постараемся ответить на него в ближайшее время.")
    await state.clear()

