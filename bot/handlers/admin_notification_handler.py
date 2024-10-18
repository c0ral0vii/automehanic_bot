from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import StateFilter, Command
from keyboards.inline.contact_keyboard import create_contact_keyboard
from keyboards.inline.admin_keyboard import create_simple_inline_navigation
from database.db_config import get_all_users, get_user
from database.models import UserRole
from aiogram.fsm.state import State, StatesGroup
from filters.chat_types import ChatTypeFilter, IsAdmin
from keyboards.reply.admin_keyboard import create_admin_navigation, create_notification_navigation
from utils.send_message import notify_user_upd


admin_router = Router(name="admin")
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())

class NotificationForm(StatesGroup):
    notification_text_all = State()
    notification_text_one = State()
    specific_user = State()

@admin_router.message(StateFilter(None), F.text == '📞 Отправить рассылку')
async def notification_handler(message: types.Message, state: FSMContext):
    keyboard = create_notification_navigation()
    await message.answer("Выберите подходящую вам опцию", reply_markup=keyboard)

@admin_router.message(StateFilter(None), F.text == 'Отправить рассылку всем пользователем')
async def auth_handler(message: types.Message, state: FSMContext):
    await message.answer("Введите текст рассылки", reply_markup=create_simple_inline_navigation())
    await state.set_state(NotificationForm.notification_text_all)

@admin_router.message(StateFilter(NotificationForm.notification_text_all))
async def send_broadcast_to_all(message: types.Message, state: FSMContext):
    users = await get_all_users()

    for user in users:
        await notify_user_upd(message.bot, user.user_id, message.text, reply_markup=create_contact_keyboard())

    await message.answer("Сообщение отправлено всем пользователям!", reply_markup=create_admin_navigation())
    await state.clear()

@admin_router.message(StateFilter(None), F.text == 'Отправить рассылку определенному пользователю')
async def auth_handler(message: types.Message, state: FSMContext):
    await message.answer("Введите ID пользователя", reply_markup=create_simple_inline_navigation())
    await state.set_state(NotificationForm.specific_user)

@admin_router.callback_query(lambda c: c.data == "cancel", StateFilter(NotificationForm))
@admin_router.message(F.text == "Отмена")
async def cancel_handler(callback_query: types.Message | types.CallbackQuery, state: FSMContext):
    await state.clear()
    keyboard = create_admin_navigation()
    if isinstance(callback_query, types.CallbackQuery):
        await callback_query.message.answer("Вы вернулись в админ-панель", reply_markup=keyboard)
    else:
        await callback_query.answer("Вы вернулись в админ-панель", reply_markup=keyboard)

@admin_router.message(StateFilter(NotificationForm.specific_user))
async def ask_notification_text(message: types.Message, state: FSMContext):
    try:
        user_id = int(message.text)
        user = await get_user(user_id)

        if user:
            await state.update_data(user_id=user.user_id)
            await message.answer(f"Пользователь найден: {user.name}. Введите текст уведомления:", reply_markup=create_simple_inline_navigation())
            await state.set_state(NotificationForm.notification_text_one)
        else:
            await message.answer("Пользователь не найден. Попробуйте снова.", reply_markup=create_simple_inline_navigation())
            await state.set_state(NotificationForm.specific_user)

    except ValueError:
        await message.answer("Пожалуйста, введите действительный ID пользователя.", reply_markup=create_simple_inline_navigation())
        await state.set_state(NotificationForm.specific_user)

@admin_router.message(StateFilter(NotificationForm.notification_text_one))
async def send_notification_to_user(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("user_id")

    try:
        await notify_user_upd(message.bot, user_id, message.text, reply_markup=create_contact_keyboard())
        await message.answer(f"Сообщение отправлено пользователю с ID {user_id}!")
    except Exception as e:
        await message.answer(f"Не удалось отправить сообщение пользователю {user_id}: {str(e)}", reply_markup=create_simple_inline_navigation())

    await state.clear()
