from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from database.models import PriceLevel
from filters.chat_types import ChatTypeFilter, IsAdmin
from keyboards.reply.admin_keyboard import create_admin_navigation, create_catalog_navigation
from keyboards.inline.admin_keyboard import create_simple_inline_navigation
from database.db_config import get_all_users, get_users_with_role_cancelled, get_users_with_role_user, get_users_with_role_undefined, update_user_price_level, update_user_role


admin_router = Router(name="admin")
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())

class AdminStates(StatesGroup):
    waiting_for_one_user_id = State()
    waiting_for_group_user_ids = State()
    waiting_for_category_selection = State()
    waiting_for_all_users_confirmation = State()
    waiting_for_price_selection = State()


@admin_router.message(StateFilter(None), F.text == '📦 Изменить уровень цен')
async def catalog_handler(message: types.Message):
    keyboard = create_catalog_navigation()
    await message.answer("Выберите подходящую вам опцию", reply_markup=keyboard)

@admin_router.callback_query(lambda c: c.data == "cancel", StateFilter(AdminStates))
@admin_router.message(F.text == "Отмена")
async def cancel_handler(callback_query: types.Message | types.CallbackQuery, state: FSMContext):
    await state.clear()
    keyboard = create_admin_navigation()
    if isinstance(callback_query, types.CallbackQuery):
        await callback_query.message.answer("Вы вернулись в админ-панель", reply_markup=keyboard)
    else:
        await callback_query.answer("Вы вернулись в админ-панель", reply_markup=keyboard)

@admin_router.message(F.text == "Поменять одному пользователю")
async def change_one_user_handler(message: types.Message, state: FSMContext):
    await message.answer("Введите ID пользователя, которому нужно поменять уровень.")
    await state.set_state(AdminStates.waiting_for_one_user_id)

@admin_router.message(F.text == "Поменять группе пользователей")
async def change_group_handler(message: types.Message, state: FSMContext):
    await message.answer("Введите список ID пользователей (каждый с новой строки) для изменения уровня.")
    await state.set_state(AdminStates.waiting_for_group_user_ids)

@admin_router.message(F.text == "Поменять категории пользователей")
async def change_category_handler(message: types.Message, state: FSMContext):
    await message.answer("Введите номер категории пользователей, которой нужно изменить уровень. (1. Авторизованный, 2. В процессе обработки модераторами, 3. Не прошедшие модерацию)")
    await state.set_state(AdminStates.waiting_for_category_selection)

@admin_router.message(F.text == "Поменять всем пользователям")
async def change_all_users_handler(message: types.Message, state: FSMContext):
    await message.answer("Вы уверены, что хотите поменять уровень для всех пользователей? Отправьте 'Да' для подтверждения.")
    await state.set_state(AdminStates.waiting_for_all_users_confirmation)

@admin_router.message(StateFilter(AdminStates.waiting_for_one_user_id))
async def process_one_user_id(message: types.Message, state: FSMContext):
    user_id = message.text.strip()
    await state.update_data(user_id=user_id)

    await message.answer(f"Получен ID пользователя: {user_id}. Теперь введите новый уровень цен.", reply_markup=create_simple_inline_navigation())
    await state.set_state(AdminStates.waiting_for_price_selection)

@admin_router.message(StateFilter(AdminStates.waiting_for_group_user_ids))
async def process_group_user_ids(message: types.Message, state: FSMContext):
    user_ids = message.text.strip().split('\n')
    await state.update_data(user_ids=user_ids)

    await message.answer(f"Получены ID пользователей: {', '.join(user_ids)}. Теперь введите новый уровень цен.", reply_markup=create_simple_inline_navigation())
    await state.set_state(AdminStates.waiting_for_price_selection)

@admin_router.message(StateFilter(AdminStates.waiting_for_category_selection))
async def process_category_selection(message: types.Message, state: FSMContext):
    category = message.text.strip().lower()
    await state.update_data(category=category)

    await message.answer(f"Вы выбрали категорию: {category}. Теперь введите новый уровень цен.", reply_markup=create_simple_inline_navigation())
    await state.set_state(AdminStates.waiting_for_price_selection)

@admin_router.message(StateFilter(AdminStates.waiting_for_all_users_confirmation))
async def process_all_users_selection(message: types.Message, state: FSMContext):
    confirmation = message.text.strip().lower()
    if confirmation == 'да':
        await state.update_data(all=confirmation)
        await message.answer('Введите новый уровень цен для всех пользователей', reply_markup=create_simple_inline_navigation())
        await state.set_state(AdminStates.waiting_for_price_selection)
    await message.answer('Вы вернулись в админ-панель', reply_markup=create_admin_navigation())
    await state.clear()

@admin_router.message(StateFilter(AdminStates.waiting_for_price_selection))
async def process_price_selection(message: types.Message, state: FSMContext):
    price_level = message.text.strip()
    price_level_map = {
        '0': PriceLevel.DEFAULT,
        '1': PriceLevel.FIRST,
        '2': PriceLevel.SECOND,
        '3': PriceLevel.THIRD,
        '4': PriceLevel.FOURTH,
    }

    if price_level not in price_level_map:
        await message.answer("Пожалуйста, введите уровень цен от 0 до 4.")
        await state.set_state(AdminStates.waiting_for_price_selection)
        return

    selected_price_level = price_level_map[price_level]
    data = await state.get_data()

    if 'user_id' in data:
        user_id = data['user_id']
        result = await update_user_price_level(int(user_id), selected_price_level)

        if result:
            await message.answer(f"Уровень цен для пользователя с ID {user_id} успешно изменён на уровень {price_level}.")
        else:
            await message.answer(f"Не удалось найти пользователя с ID {user_id}.")

    elif 'user_ids' in data:
        user_ids = data['user_ids']
        for user_id in user_ids:
            result = await update_user_price_level(int(user_id), selected_price_level)
            if result:
                await message.answer(f"Уровень цен для пользователя с ID {user_id} успешно изменён на уровень {price_level}.")
            else:
                await message.answer(f"Не удалось изменить уровень цен для пользователя с ID {user_id}.")

    elif 'category' in data:
        category = data['category']
        if category == "1":
            users = await get_users_with_role_user()
        elif category == "2":
            users = await get_users_with_role_undefined()
        elif category == "3":
            user = await get_users_with_role_cancelled()
        else:
            await message.answer("Категория не распознана.")
            return

        for user in users:
            result = await update_user_price_level(int(user.user_id), selected_price_level)
            if result:
                await message.answer(f"Уровень цен для пользователя {user.name} {user.surname} успешно изменён на уровень {price_level}.")
            else:
                await message.answer(f"Не удалось изменить уровень цен для пользователя {user.name} {user.surname}.")

    elif 'all' in data:
        all_users = await get_all_users()
        for user in all_users:
            result = await update_user_price_level(int(user.user_id), selected_price_level)
            if result:
                await message.answer(f"Уровень цен для пользователя {user.name} {user.surname} успешно изменён на уровень {price_level}.")
            else:
                await message.answer(f"Не удалось изменить уровень цен для пользователя {user.name} {user.surname}.")

    await state.clear()
    await message.answer("Изменение уровня цен завершено.", reply_markup=create_admin_navigation())

