from aiogram import Router, types
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from keyboards.reply.main_keyboard import create_main_keyboard
from database.db_config import check_auth


start_router = Router(name="start")


@start_router.message(CommandStart(), StateFilter(None))
async def start_handler(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    check = await check_auth(user_id=message.from_user.id)
    keyboard = create_main_keyboard(auth=check)

    await message.answer(
        """Приветствую! 👋  
Я – бот-помощник MARSHALL.OFF-HIGHWAY 🚜.  
Здесь вы найдете качественные запчасти от бренда MARSHALL для строительной и сельскохозяйственной техники в наличии и под заказ 🛠.""",
        reply_markup=keyboard,
    )

    await message.answer(
        """• Отправьте артикул, чтобы узнать о стоимости и наличии необходимой детали на нашем складе. 🏷  
• Изучите информацию по артикулу, чтобы понять, подходит он вам или нет. 🔍  
• Чтобы видеть актуальные цены, вы можете авторизоваться (если уже являетесь нашим клиентом) или направить нам запрос на добавление вашей компании в ряды партнеров и получить персональное предложение! 💼  

• 🌐 Наш сайт – off-highway.marshall.parts  
• 🚜 Запчасти для строительной, сельскохозяйственной и лесозаготовительной техники в наличии и под заказ.  
• 🤝 Помощь в подборе.  
• 🚚 Доставка во все регионы России и стран СНГ."""
    )
