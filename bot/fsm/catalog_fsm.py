from aiogram.fsm.state import State, StatesGroup


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