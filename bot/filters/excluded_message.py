from aiogram.fsm.context import FSMContext
from aiogram.filters import Filter
from aiogram import types
from fsm.catalog_fsm import Form
from fsm.auth_fsm import AuthForm

class ExcludedMessage(Filter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: types.Message, state: FSMContext) -> bool:
        excluded_message = ['👨‍🦱Мой профиль', '📑 Презентации по продукту', '📞 Связаться с нами']
        if await state.get_state():
            excluded_message.append('📦 Каталог')
            excluded_message.append('🔐 Авторизоваться')


        if message.text not in excluded_message:
            return True
        await state.clear()
        return False