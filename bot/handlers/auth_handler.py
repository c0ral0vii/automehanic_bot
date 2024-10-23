from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter, Command
from database.db_config import add_user, check_user_role
from utils.validation import validate_phone_number
from keyboards.reply.main_keyboard import create_main_keyboard
from keyboards.inline.auth_keyboard import create_inline_navigation_keyboard
from fsm.auth_fsm import AuthForm
from filters.excluded_message import ExcludedMessage


auth_router = Router(name="auth")
auth_router.message.filter(ExcludedMessage())

@auth_router.message(StateFilter(None), F.text == '🔐 Авторизоваться')
async def auth_handler(message: types.Message, state: FSMContext):
    keyboard = create_inline_navigation_keyboard()

    await message.answer("Введите ваше имя:", reply_markup=keyboard)
    await state.set_state(AuthForm.name)

@auth_router.callback_query(lambda c: c.data == "cancel", StateFilter(AuthForm))
@auth_router.message(Command("cancel"), StateFilter(AuthForm))
async def cancel_handler(callback_query: types.CallbackQuery | types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()

    keyboard = create_main_keyboard()
    if isinstance(callback_query, types.CallbackQuery):
        await callback_query.message.answer("Действия отменены", reply_markup=keyboard)
    else:
        await callback_query.answer("Действия отменены", reply_markup=keyboard)

@auth_router.callback_query(lambda c: c.data == "back", StateFilter(AuthForm))
@auth_router.message(Command("back"), StateFilter(AuthForm))
async def back_step_handler(callback_query: types.CallbackQuery | types.Message, state: FSMContext):
    current_state = await state.get_state()
    previous = None
    keyboard = create_inline_navigation_keyboard()

    if current_state == AuthForm.name:
        if isinstance(callback_query, types.CallbackQuery):
            await callback_query.message.answer('Предыдущего шага нет, или введите имя или нажмите "Отмена":', reply_markup=keyboard)
        else:
            await callback_query.answer('Предыдущего шага нет, или введите имя или нажмите "Отмена":', reply_markup=keyboard)
        return

    for step in AuthForm.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            if isinstance(callback_query, types.CallbackQuery):
                await callback_query.message.answer(f"Ок, вы вернулись к прошлому шагу \n{AuthForm.texts[previous.state]}", reply_markup=keyboard)
            else:
                await callback_query.answer(f"Ок, вы вернулись к прошлому шагу \n{AuthForm.texts[previous.state]}", reply_markup=keyboard)
            return
        previous = step

@auth_router.message(AuthForm.name)
async def process_name(message: types.Message, state: FSMContext):
    name = message.text.strip()

    if not name:
        await message.answer("Имя не может быть пустым. Пожалуйста, введите корректное имя:")
        return

    await state.update_data(name=name)
    keyboard = create_inline_navigation_keyboard()
    await message.answer("Введите вашу фамилию:", reply_markup=keyboard)
    await state.set_state(AuthForm.surname)

@auth_router.message(AuthForm.surname)
async def process_surname(message: types.Message, state: FSMContext):
    surname = message.text.strip()

    if not surname:
        await message.answer("Фамилия не может быть пустой. Пожалуйста, введите корректную фамилию:")
        return

    await state.update_data(surname=surname)
    keyboard = create_inline_navigation_keyboard()
    await message.answer("Введите название вашей организации:", reply_markup=keyboard)
    await state.set_state(AuthForm.organization_name)

@auth_router.message(AuthForm.organization_name)
async def process_organization_name(message: types.Message, state: FSMContext):
    organization_name = message.text.strip()

    if not organization_name:
        await message.answer("Название организации не может быть пустым. Пожалуйста, введите корректное название:")
        return

    await state.update_data(organization_name=organization_name)
    keyboard = create_inline_navigation_keyboard()
    await message.answer("Введите ваш номер телефона (например, +79991234567):", reply_markup=keyboard)
    await state.set_state(AuthForm.phone_number)

@auth_router.message(AuthForm.phone_number)
async def process_phone_number(message: types.Message, state: FSMContext):
    phone_number = message.text.strip()

    if not validate_phone_number(phone_number):
        await message.answer("Некорректный номер телефона. Пожалуйста, введите номер в формате +79991234567:")
        return

    user_data = await state.get_data()
    user_id = message.from_user.id

    user_role = await check_user_role(user_id)

    if user_role == 'user':
        await message.answer("Вы уже авторизовались.")
        await state.clear()
        return

    user_added = await add_user(
        user_id=user_id,
        name=user_data['name'],
        surname=user_data['surname'],
        organization_name=user_data['organization_name'],
        phone_number=phone_number
    )

    if user_added:
        await message.answer("Спасибо за запрос на авторизацию! Ваше сообщение отправлено, администратор скоро его обработает. Ожидайте подтверждение.")
    else:
        await message.answer("Ваша заявка уже находиться на рассмотрении у модераторов")

    await state.clear()






