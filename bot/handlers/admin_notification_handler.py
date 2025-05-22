from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import StateFilter, Command
from keyboards.inline.contact_keyboard import create_contact_keyboard
from keyboards.inline.admin_keyboard import create_simple_inline_navigation, create_user_list_keyboard
from database.db_config import get_all_users, get_user
from database.models import UserRole
from aiogram.fsm.state import State, StatesGroup
from filters.chat_types import ChatTypeFilter, IsAdmin
from keyboards.reply.admin_keyboard import (
    create_admin_navigation,
    create_notification_navigation,
)
from utils.send_message import notify_user_upd


admin_router = Router(name="admin")
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())


class NotificationForm(StatesGroup):
    notification_text_all = State()
    notification_text_one = State()
    specific_user = State()


@admin_router.message(StateFilter(None), F.text == "📞 Отправить рассылку")
async def notification_handler(message: types.Message, state: FSMContext):
    keyboard = create_notification_navigation()
    await message.answer("Выберите подходящую вам опцию", reply_markup=keyboard)


@admin_router.message(
    StateFilter(None), F.text == "Отправить рассылку всем пользователем"
)
async def auth_handler(message: types.Message, state: FSMContext):
    await message.answer(
        "Введите текст рассылки", reply_markup=create_simple_inline_navigation()
    )
    await state.set_state(NotificationForm.notification_text_all)


@admin_router.message(StateFilter(NotificationForm.notification_text_all))
async def send_broadcast_to_all(message: types.Message, state: FSMContext):
    users = await get_all_users()

    for user in users:
        await notify_user_upd(
            message.bot,
            user.user_id,
            message.text,
            reply_markup=create_contact_keyboard(),
        )

    await message.answer(
        "Сообщение отправлено всем пользователям!",
        reply_markup=create_admin_navigation(),
    )
    await state.clear()


@admin_router.message(
    StateFilter(None), F.text == "Отправить рассылку определенному пользователю"
)
async def auth_handler(message: types.Message, state: FSMContext):
    users = await get_all_users()
    total_users = len(users)
    users_per_page = 5
    total_pages = (total_users + users_per_page - 1) // users_per_page
    current_page = 1
    
    page_users = users[
        (current_page - 1) * users_per_page : current_page * users_per_page
    ]
    keyboard = create_user_list_keyboard(page_users, current_page, total_pages)
    
    await message.answer(
        "Выберите пользователя:", reply_markup=keyboard
    )
    
    await state.set_state(NotificationForm.specific_user) 


@admin_router.callback_query(
    lambda c: c.data.startswith("page_"),
    StateFilter(NotificationForm.specific_user),
)
async def paginate_user_list(callback_query: types.CallbackQuery, state: FSMContext):
    current_page = int(callback_query.data.split("_")[1])

    users = await get_all_users()
    total_users = len(users)
    users_per_page = 5
    total_pages = (total_users + users_per_page - 1) // users_per_page

    page_users = users[
        (current_page - 1) * users_per_page : current_page * users_per_page
    ]

    keyboard = create_user_list_keyboard(page_users, current_page, total_pages)
    await callback_query.message.edit_reply_markup(reply_markup=keyboard)
    
    
@admin_router.callback_query(
    lambda c: c.data == "cancel", StateFilter(NotificationForm),
)
@admin_router.message(F.text == "Отмена")
async def cancel_handler(
    callback_query: types.Message | types.CallbackQuery, state: FSMContext
):
    await state.clear()
    keyboard = create_admin_navigation()
    if isinstance(callback_query, types.CallbackQuery):
        await callback_query.message.answer(
            "Вы вернулись в админ-панель", reply_markup=keyboard
        )
    else:
        await callback_query.answer(
            "Вы вернулись в админ-панель", reply_markup=keyboard
        )


@admin_router.callback_query(F.data.startswith("user_"),
                      StateFilter(NotificationForm.specific_user))
async def ask_notification_text(callback: types.CallbackQuery, state: FSMContext):
    try:
        user_id = callback.data.split("_")[-1]
        user = await get_user(int(user_id))
        await state.update_data(user_id=user_id)

        await callback.message.answer(
            f"Выбран пользователь: {user.name}. Введите текст уведомления:",
            reply_markup=create_simple_inline_navigation(),
        )
        await state.set_state(NotificationForm.notification_text_one)

    except ValueError:
        await callback.message.answer(
            "Пожалуйста, введите действительный ID пользователя.",
            reply_markup=create_simple_inline_navigation(),
        )
        
        await state.set_state(NotificationForm.specific_user)


@admin_router.message(StateFilter(NotificationForm.notification_text_one))
async def send_notification_to_user(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("user_id")

    try:
        await notify_user_upd(
            message.bot, user_id, message.text, reply_markup=create_contact_keyboard()
        )
        await message.answer(f"Сообщение отправлено пользователю с ID {user_id}!")
    except Exception as e:
        await message.answer(
            f"Не удалось отправить сообщение пользователю {user_id}: {str(e)}",
            reply_markup=create_simple_inline_navigation(),
        )

    await state.clear()
