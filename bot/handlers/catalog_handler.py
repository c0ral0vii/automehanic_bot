from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter, Command
from database.db_config import get_product, get_price_for_user
from keyboards.inline.catalog_keyboard import create_catalog_keyboard, create_product_keyboard, create_simple_inline_navigation
from keyboards.reply.main_keyboard import create_main_keyboard
from utils.texts import get_greeting_text
from sqlalchemy.exc import NoResultFound
from utils.send_email import send_order_email
import pandas as pd

catalog_router = Router(name="catalog")

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


@catalog_router.callback_query(lambda c: c.data == "request_single_article")
async def handle_single_article_request(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите артикул:", reply_markup=create_simple_inline_navigation())
    await state.set_state(Form.article)

@catalog_router.callback_query(lambda c: c.data == "request_multiple_articles")
async def handle_multiple_articles_request(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Для обработки списка артикулов, пришлите файл в формате Excel (Первый столбец - артикул, название для столбца не нужно), или через сообщение в таком формате:\nФормат: артикул (в столбик)")
    await state.set_state(Form.multiple_articles)

@catalog_router.callback_query(lambda c: c.data == "cancel", StateFilter(Form))
@catalog_router.message(Command("cancel"), StateFilter(Form))
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

@catalog_router.callback_query(lambda c: c.data == "back", StateFilter(Form))
@catalog_router.message(Command("back"), StateFilter(Form))
async def back_step_handler(callback_query: types.CallbackQuery | types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    keyboard = create_simple_inline_navigation()
    previous = None

    if current_state == Form.article:
        if isinstance(callback_query, types.CallbackQuery):
            await callback_query.message.answer('Введите артикул:', reply_markup=keyboard)
        else:
            await callback_query.answer('Введите артикул:', reply_markup=keyboard)
        return

    if current_state == Form.multiple_articles:
        if isinstance(callback_query, types.CallbackQuery):
            await callback_query.message.answer("Для обработки списка артикулов, пришлите файл в формате Excel (Первый столбец - артикул, название для столбца не нужно)," \
                                         " или через сообщение в таком формате: Формат: артикул (в столбик)", reply_markup=keyboard)
        else:
            await callback_query.answer("Для обработки списка артикулов, пришлите файл в формате Excel (Первый столбец - артикул, название для столбца не нужно)," \
                                         " или через сообщение в таком формате: Формат: артикул (в столбик)", reply_markup=keyboard)
        return

    for step in Form.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            if isinstance(callback_query, types.CallbackQuery):
                await callback_query.message.answer(f"Ок, вы вернулись к прошлому шагу \n {Form.texts[previous.state]}", reply_markup=keyboard)
            else:
                await callback_query.answer(f"Ок, вы вернулись к прошлому шагу \n {Form.texts[previous.state]}", reply_markup=keyboard)
            return
        previous = step

@catalog_router.message(Form.article, F.text)
async def process_article_input(message: types.Message, state: FSMContext):
    await state.update_data(article=message.text)
    data = await state.get_data()
    article_number = data['article'].strip()
    user_id = message.from_user.id

    try:
        price = await get_price_for_user(user_id, article_number)

        if price is None:
            await message.answer("Товар не найден или цена недоступна.")
            return

        product = await get_product(article_number)

        if product is not None:
            response_text = (
                f"Артикул: {product.article_number}\n"
                f"Название: {product.name}\n"
                f"Наличие: {product.amount}\n"
                f"Цена: {price}\n\n"
                "Указанная цена может меняться в меньшую сторону в зависимости от суммы заказа и Вашего уровня цен. "
                "После размещения заявки с Вами свяжется наш менеджер и уточнит все детали."
            )
            keyboard = create_product_keyboard()
            await message.answer(response_text, reply_markup=keyboard)
        else:
            await message.answer("Товар не найден. Пожалуйста, проверьте артикул и попробуйте снова.")
    except NoResultFound:
        await message.answer("Произошла ошибка при получении данных о товаре.")

@catalog_router.message(Form.multiple_articles, F.document)
async def process_xlsx_file(message: types.Message, state: FSMContext):
    document_id = message.document.file_id
    document = await message.bot.get_file(document_id)

    file_path = await message.bot.download_file(document.file_path)

    try:
        df = pd.read_excel(file_path, header=None, engine='openpyxl')
        df.columns = ['Артикул']

        response = []
        user_id = message.from_user.id

        for index, row in df.iterrows():
            article_number = str(row['Артикул']).strip()
            price = await get_price_for_user(user_id, article_number)

            product = await get_product(article_number)
            if product and price:
                response.append(
                    f"Артикул: {product.article_number}\n"
                    f"Название: {product.name}\n"
                    f"Наличие: {product.amount}\n"
                    f"Цена: {price}\n\n"
                )
            else:
                response.append(f"Товар с артикулом {article_number} не найден.\n")

        keyboard = create_product_keyboard()
        await message.answer(''.join(response), reply_markup=keyboard)

    except Exception as e:
        await message.answer(f"Произошла ошибка при обработке файла: {str(e)}.\nОтправьте файл заново.")
        await state.set_state(Form.multiple_articles)

@catalog_router.message(Form.multiple_articles, F.text)
async def process_multiple_articles_input(message: types.Message, state: FSMContext):
    articles_data = message.text.strip().split('\n')
    response = []
    user_id = message.from_user.id

    for article_number in articles_data:
        article_number = article_number.strip()
        if not article_number:
            continue
        price = await get_price_for_user(user_id, article_number)
        product = await get_product(article_number)
        if product and price:
            response.append(
                f"Артикул: {product.article_number}\n"
                f"Название: {product.name}\n"
                f"Наличие: {product.amount}\n"
                f"Цена: {price}\n\n"
            )
        else:
            response.append(f"Товар с артикулом {article_number} не найден.\n")

    if not response:
        await message.answer("Не найдено ни одного товара по указанным артикулам.")
    else:
        keyboard = create_product_keyboard()
        await message.answer(''.join(response), reply_markup=keyboard)

@catalog_router.message(Form.article_quantity_input, F.text)
async def process_article_quantity_text_input(message: types.Message, state: FSMContext):
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
    keyboard = create_main_keyboard()
    await message.answer("Ваш заказ находится в обработке. Пожалуйста, укажите ваши контактные данные: ФИО и номер телефона в формате (ФИО, номер телефона), чтобы менеджер мог уточнить информацию по заказу.", reply_markup=keyboard)
    await state.set_state(Form.contact_info)

@catalog_router.message(Form.article_quantity_input, F.document)
async def process_article_quantity_xlsx_input(message: types.Message, state: FSMContext):
    document_id = message.document.file_id
    document = await message.bot.get_file(document_id)
    file_path = await message.bot.download_file(document.file_path)

    try:
        df = pd.read_excel(file_path, header=None, engine='openpyxl')
        df.columns = ['Артикул', 'Количество']

        orders = []
        for index, row in df.iterrows():
            article_number = str(row['Артикул']).strip()
            quantity = int(row['Количество'])
            orders.append({'article': article_number, 'quantity': quantity})

        await state.update_data(orders=orders)
        keyboard = create_main_keyboard()
        await message.answer("Ваш заказ находится в обработке. Пожалуйста, укажите ваши контактные данные: ФИО и номер телефона в формате (ФИО, номер телефона), чтобы менеджер мог уточнить информацию по заказу.", reply_markup=keyboard)
        await state.set_state(Form.contact_info)

    except Exception as e:
        await message.answer(f"Произошла ошибка при обработке файла: {str(e)}")
        await state.clear()

@catalog_router.callback_query(lambda c: c.data == "order_request")
async def handle_order_request(callback_query: types.CallbackQuery, state: FSMContext):
    keyboard = create_simple_inline_navigation()
    await callback_query.message.answer(
        "Пожалуйста, введите артикулы и количество в следующем формате:\n\n"
        "- (артикул; количество)\n\n"
        "Каждый новый артикул с новой строки, либо отправьте файл в формате Excel (Первый столбец - артикль, второй - количество, названия для столбцов не нужны).", reply_markup=keyboard
    )
    await state.set_state(Form.article_quantity_input)

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

    keyboard = create_main_keyboard()

    await message.answer("Спасибо! Ваш заказ отправлен. Менеджер скоро с вами свяжется.", reply_markup=keyboard)
    await state.clear()

