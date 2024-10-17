from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from database.config import get_product
from keyboards.inline.catalog_keyboard import create_catalog_keyboard, create_product_keyboard, create_inline_navigation_keyboard
from utils.texts import get_greeting_text
from utils.send_email import send_order_email

catalog_router = Router(name="catalog")

texts = {
    'AddProduct:name': 'Введите артикль заново:'
}

@catalog_router.message(StateFilter(None), F.text == '📦 Каталог')
async def catalog_handler(message: types.Message):
    text = get_greeting_text()
    keyboard = create_catalog_keyboard()
    await message.answer(text, reply_markup=keyboard)

class Form(StatesGroup):
    article = State()
    multiple_articles = State()
    article_quantity_input = State()
    contact_info = State()

    texts = {
        'Form.article': 'Введите артикул заново:',
        'Form.multiple_articles': 'Для обработки списка артикулов, пришлите файл в формате Excel, или через сообщение в таком формате:\n\nФормат: артикул (в столбик)',
        'Form.article_quantity_input': 'Введите артикулы и количество в формате: (артикул; количество)',
        'Form.contact_info': 'Пожалуйста, укажите ваши контактные данные: ФИО и номер телефона в формате (ФИО, номер телефона), чтобы менеджер мог уточнить информацию по заказу.'
    }


# inline keyboard callbacks
@catalog_router.callback_query(lambda c: c.data == "request_single_article")
async def handle_single_article_request(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите артикул:", reply_markup=create_inline_navigation_keyboard())
    await state.set_state(Form.article)

@catalog_router.callback_query(lambda c: c.data == "request_multiple_articles")
async def handle_multiple_articles_request(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.reply("Для обработки списка артикулов, пришлите файл в формате Excel, или через сообщение в таком формате:\n\nФормат: артикул (в столбик)")
    await state.set_state(Form.multiple_articles)

@catalog_router.callback_query(lambda c: c.data == "order_request")
async def handle_order_request(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer(
        "Пожалуйста, введите артикулы и количество в следующем формате:\n\n"
        "- (артикул; количество)\n\n"
        "Каждый новый артикул с новой строки, либо отправьте файл в формате Excel."
    )
    await state.set_state(Form.article_quantity_input)


# fsm and cancel handlers
@catalog_router.callback_query(lambda c: c.data == "cancel")
async def cancel_handler(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await callback_query.message.answer("Действия отменены")

@catalog_router.callback_query(lambda c: c.data == "back")
async def back_step_handler(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    current_state = await state.get_state()
    keyboard = create_catalog_keyboard()

    if current_state == Form.article:
        await callback_query.message.answer(f'Ок, вы вернулись к прошлому шагу. Введите артикул', reply_markup=keyboard)
        return

    previous = None
    for step in Form.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await callback_query.answer(f"Ок, вы вернулись к прошлому шагу \n {Form.texts[previous.state]}")
            return
        previous = step

@catalog_router.message(Form.article, F.text)
async def process_article_input(message: types.Message, state: FSMContext):
    await state.update_data(article=message.text)
    data = await state.get_data()
    article_number = data['article']

    article_number = message.text.strip()
    product = await get_product(article_number)
    if product is not None:
        response_text = (
            f"Артикул: {product.article_number}\n"
            f"Название: {product.name}\n"
            f"Наличие: {product.amount}\n"
            f"Цена: {product.price}\n\n"
            "Указанная цена может меняться в меньшую сторону в зависимости от суммы заказа и Вашего уровня цен. "
            "После размещения заявки с Вами свяжется наш менеджер и уточнит все детали."
        )
        keyboard = create_product_keyboard()
        await message.answer(response_text, reply_markup=keyboard)
    else:
        await message.answer("Товар не найден. Пожалуйста, проверьте артикул и попробуйте снова.")

@catalog_router.message(Form.multiple_articles, F.text)
async def process_multiple_articles_input(message: types.Message, state: FSMContext):
    articles = message.text.strip().split('\n')
    response = []
    for article_number in articles:
        product = await get_product(article_number.strip())
        if product:
            response.append(
                f"Артикул: {product.article_number}\n"
                f"Название: {product.name}\n"
                f"Наличие: {product.amount}\n"
                f"Цена: {product.price}\n\n"
            )
        else:
            response.append(f"Товар с артикулом {article_number.strip()} не найден.\n")

    keyboard = create_product_keyboard()
    await message.answer(''.join(response), reply_markup=keyboard)

@catalog_router.message(Form.article_quantity_input, F.text)
async def process_article_quantity_input(message: types.Message, state: FSMContext):
    articles_data = message.text.strip().split('\n')

    orders = []
    for item in articles_data:
        try:
            article, quantity = item.split(';')
            orders.append({
                'article': article.strip(),
                'quantity': int(quantity.strip())
            })
        except ValueError:
            await message.answer("Ошибка формата. Пожалуйста, введите артикулы и количество в формате: (артикул; количество)")
            return

    await state.update_data(orders=orders)
    await message.answer("Ваш заказ находится в обработке. Пожалуйста, укажите ваши контактные данные: ФИО и номер телефона в формате (ФИО, номер телефона), чтобы менеджер мог уточнить информацию по заказу.")
    await state.set_state(Form.contact_info)

@catalog_router.message(Form.contact_info, F.text)
async def process_contact_info(message: types.Message, state: FSMContext):
    contact_info = message.text.strip()
    data = await state.get_data()
    orders = data.get('orders', [])

    order_message = "Новый заказ:\n\n"
    for order in orders:
        order_message += f"Артикул: {order['article']}, Количество: {order['quantity']}\n"

    order_message += f"\nКонтактная информация:\n{contact_info}"

    user_id = message.from_user.id
    username = message.from_user.username or "Неизвестный пользователь"
    order_items = [(order['article'], order['quantity']) for order in orders]

    await send_order_email(user_id, username, order_items, contact_info)

    await message.answer("Спасибо! Ваш заказ отправлен. Менеджер скоро с вами свяжется.")
    await state.clear()

