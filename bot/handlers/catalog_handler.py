from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.inline.catalog_keyboard import create_catalog_keyboard
from utils.texts import get_greeting_text

catalog_router = Router(name="catalog")

class Form(StatesGroup):
    waiting_for_article = State()

@catalog_router.message(F.text == '📦 Каталог')
async def catalog_handler(message: types.Message):
    text = get_greeting_text()
    keyboard = create_catalog_keyboard()
    await message.answer(text, reply_markup=keyboard)

@catalog_router.message(F.text & F.state(Form.waiting_for_article))
async def process_article_input(message: types.Message, state: FSMContext):
    try:
        article_number = message.text.strip()
        product_info = await get_product_info(article_number)
        if product_info:
            response_text = (
                f"Артикул: {product_info['article_number']}\n"
                f"Название: {product_info['name']}\n"
                f"Наличие: {product_info['amount']}\n"
                f"Цена: {product_info['price']}\n\n"
                "Указанная цена может меняться в меньшую сторону в зависимости от суммы заказа и Вашего уровня цен. "
                "После размещения заявки с Вами свяжется наш менеджер и уточнит все детали."
            )
            await message.answer(response_text)
        else:
            await message.answer("Товар не найден. Пожалуйста, проверьте артикул и попробуйте снова.")
    except Exception as e:
        print(f"Ошибка при обработке артикул: {e}")
        await message.answer("Произошла ошибка при обработке вашего запроса. Попробуйте снова.")

@catalog_router.callback_query(lambda c: c.data == "request_single_article")
async def handle_single_article_request(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.reply("Введите артикул:")
    await state.set_state(Form.waiting_for_article)

@catalog_router.callback_query(lambda c: c.data == "request_multiple_articles")
async def handle_multiple_articles_request(callback_query: types.CallbackQuery):
    await callback_query.message.reply("Для обработки списка артикулов, пришлите файл в формате Excel, или через сообщение в таком формате:\n\nФормат: артикул (в столбик)")

async def get_product_info(article_number: str):
    dummy_product_data = {
        'article_number': '12345',
        'name': 'Пример товара',
        'amount': '3',
        'price': '1000 ₽'
    }

    if article_number == '12345':
        return dummy_product_data
    return None