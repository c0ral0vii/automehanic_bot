from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from bot.database.config import add_user
from utils.validation import validate_phone_number

auth_router = Router(name="auth")

class AuthForm(StatesGroup):
    name = State()
    surname = State()
    organization_name = State()
    phone_number = State()


@auth_router.message(StateFilter(None), F.text == '🔐 Авторизоваться')
async def auth_handler(message: types.Message, state: FSMContext):
    await message.answer("Введите ваше имя:")
    await state.set_state(AuthForm.name)

@auth_router.message(AuthForm.name)
async def process_name(message: types.Message, state: FSMContext):
    name = message.text.strip()

    if not name:
        await message.answer("Имя не может быть пустым. Пожалуйста, введите корректное имя:")
        return

    await state.update_data(name=name)
    await message.answer("Введите вашу фамилию:")
    await state.set_state(AuthForm.surname)

@auth_router.message(AuthForm.surname)
async def process_surname(message: types.Message, state: FSMContext):
    surname = message.text.strip()

    if not surname:
        await message.answer("Фамилия не может быть пустой. Пожалуйста, введите корректную фамилию:")
        return

    await state.update_data(surname=surname)
    await message.answer("Введите название вашей организации:")
    await state.set_state(AuthForm.organization_name)

@auth_router.message(AuthForm.organization_name)
async def process_organization_name(message: types.Message, state: FSMContext):
    organization_name = message.text.strip()

    if not organization_name:
        await message.answer("Название организации не может быть пустым. Пожалуйста, введите корректное название:")
        return

    await state.update_data(organization_name=organization_name)
    await message.answer("Введите ваш номер телефона (например, +79991234567):")
    await state.set_state(AuthForm.phone_number)

@auth_router.message(AuthForm.phone_number)
async def process_phone_number(message: types.Message, state: FSMContext):
    phone_number = message.text.strip()

    if not validate_phone_number(phone_number):
        await message.answer("Некорректный номер телефона. Пожалуйста, введите номер в формате +79991234567:")
        return

    await state.update_data(phone_number=phone_number)

    user_data = await state.get_data()

    await add_user(
        user_id=message.from_user.id,
        username=user_data['name'],
        fullname=user_data['surname'],
        phone=user_data['phone_number']
    )

    await message.answer("Вы успешно авторизовались!")
    await state.clear()
