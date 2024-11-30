from aiogram.fsm.state import State, StatesGroup


class AuthForm(StatesGroup):
    name = State()
    surname = State()
    organization_name = State()
    phone_number = State()

    texts = {
        'AuthForm:name': 'Введите имя заново:',
        'AuthForm:surname': 'Введите фамилию заново:',
        'AuthForm:organization_name': 'Введите организацию заново:',
        'AuthForm:phone_number': 'Этот стейт последний, поэтому...',
    }