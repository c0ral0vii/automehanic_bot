from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import StateFilter, Command
from database.models import UserRole
from filters.chat_types import ChatTypeFilter, IsAdmin
from keyboards.reply.admin_keyboard import create_admin_navigation, create_auth_navigation
from database.db_config import get_all_users, get_users_with_role_user, get_users_with_role_undefined, update_catalog, update_user_role
from utils.send_message import notify_user


admin_router = Router(name="admin")
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())

@admin_router.message(Command("admin"))
async def admin_features(message: types.Message):
    keyboard = create_admin_navigation()
    await message.answer("Что хотите сделать?", reply_markup=keyboard)

@admin_router.message(Command("cancel"))
@admin_router.message(F.text == 'Отмена')
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    keyboard = create_admin_navigation()
    await message.answer("Вы вернулись в админ-панель", reply_markup=keyboard)

@admin_router.callback_query(lambda cb: cb.data.startswith('accept_'))
async def accept_request(callback_query: types.CallbackQuery):
    user_id = int(callback_query.data.split('_')[1])
    await update_user_role(user_id, UserRole.USER)
    await callback_query.answer("Запрос принят.")
    await callback_query.message.delete()
    welcome_message = (
        "Здравствуйте! Ваш запрос на регистрацию успешно прошел модерацию. "
        "Добро пожаловать! Вы можете начать использовать все возможности нашей платформы."
    )
    await notify_user(callback_query.bot, user_id, welcome_message)

@admin_router.callback_query(lambda cb: cb.data.startswith('reject_'))
async def reject_request(callback_query: types.CallbackQuery):
    user_id = int(callback_query.data.split('_')[1])
    await update_user_role(user_id, UserRole.CANCELLED)
    await callback_query.answer("Запрос отклонён.")
    await callback_query.message.delete()
    rejection_message = (
        "Здравствуйте! К сожалению, ваша регистрация не прошла модерацию. "
        "Если у вас есть вопросы или вы хотите уточнить причины, пожалуйста, свяжитесь с нами."
    )
    await notify_user(callback_query.bot, user_id, rejection_message)

@admin_router.message(StateFilter(None), F.text == '🔐 Авторизация')
async def catalog_handler(message: types.Message):
    keyboard = create_auth_navigation()
    await message.answer("Выберите подходящую вам опцию", reply_markup=keyboard)

@admin_router.message(StateFilter(None), F.text == 'Запросы на авторизацию')
async def all_requests_handler(message: types.Message):
    users = await get_users_with_role_undefined()
    if users:
        for i, user in enumerate(users):
            user_info = (
                f"{i + 1}. {user.name} {user.surname}\n"
                f"   Организация: {user.organization_name}\n"
                f"   Телефон: {user.phone_number}\n"
                f"   (ID: {user.user_id})"
            )

            accept = InlineKeyboardButton(text="Принять", callback_data=f"accept_{user.user_id}")
            reject = InlineKeyboardButton(text="Отклонить", callback_data=f"reject_{user.user_id}")

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [accept, reject]
            ])
            await message.answer(user_info, reply_markup=keyboard)
    else:
        await message.answer("Нет неавторизованных пользователей.")

@admin_router.message(StateFilter(None), F.text == 'Все пользователи')
async def all_users_handler(message: types.Message):
    users = await get_all_users()
    if users:
        user_list = "Список пользователей:\n\n"
        user_list += "\n".join([
            f"{i + 1}. {user.name} {user.surname}\n"
            f"   Организация: {user.organization_name}\n"
            f"   Телефон: {user.phone_number}\n"
            f"   Роль: {'Администратор' if user.role == 'admin' else 'Пользователь' if user.role == 'user' else 'Неопределённый' if user.role == 'undefined' else 'Отменённый'}\n"
            f"   Уровень цен: {'Первый' if user.price_level == 'first' else 'Второй' if user.price_level == 'second' else 'Третий' if user.price_level == 'third' else 'Четвёртый' if user.price_level == 'fourth' else 'Стандартный'}\n"
            f"   (ID: {user.user_id})\n"
            for i, user in enumerate(users)
        ])

        max_message_length = 4096
        if len(user_list) > max_message_length:
            chunks = [user_list[i:i + max_message_length] for i in range(0, len(user_list), max_message_length)]
            for chunk in chunks:
                await message.answer(chunk)
        else:
            await message.answer(user_list)
    else:
        await message.answer("Нет зарегистрированных пользователей.")


@admin_router.message(StateFilter(None), F.text == 'Все авторизованные пользователи')
async def all_authenticated_users_handler(message: types.Message):
    users = await get_users_with_role_user()
    if users:
        user_list = "\n\n".join([
            f"{i + 1}. {user.name} {user.surname}\n"
            f"   Организация: {user.organization_name}\n"
            f"   Телефон: {user.phone_number}\n"
            f"   Роль: {'Администратор' if user.role == 'admin' else 'Пользователь' if user.role == 'user' else 'Неопределённый' if user.role == 'undefined' else 'Отменённый'}\n"
            f"   Уровень цен: {'Первый' if user.price_level == 'first' else 'Второй' if user.price_level == 'second' else 'Третий' if user.price_level == 'third' else 'Четвёртый' if user.price_level == 'fourth' else 'Стандартный'}\n"
            f"   (ID: {user.user_id})"
            for i, user in enumerate(users)
        ])

        max_message_length = 4096
        if len(user_list) > max_message_length:
            chunks = [user_list[i:i + max_message_length] for i in range(0, len(user_list), max_message_length)]
            for chunk in chunks:
                await message.answer(chunk)
        else:
            await message.answer(f"Все авторизованные пользователи:\n\n{user_list}")
    else:
        await message.answer("Нет авторизованных пользователей.")



@admin_router.message(StateFilter(None), F.text == '🔃Обновить каталог')
async def reload_catalog(message: types.Message):
    try:
        await update_catalog()
        await message.answer(f'Каталог обновлён✅')
    except FileNotFoundError:
        await message.answer(f'Возникла ошибка❌\nПоместите файл в bot/utils/data/catalog/data.xlsx')

    #TO-DO: Работает для добавления данных в бд с нуля, но нет обновления, легко реализовать update_product() и так же