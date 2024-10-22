from aiogram import Router, types, F
from database.db_config import my_profile


profile_router = Router(name='my_profile')


@profile_router.message(F.text == '👨‍🦱Мой профиль')
async def check_profile(message: types.Message):
    '''
    Открытие профиля пользователем
    '''

    data = await my_profile(user_id=message.from_user.id)
    if data:
        await message.answer(f"👨‍🦱Мой профиль:\nВаше имя: {data.get('name', 'Не указано')}\nВаша фамилия: {data.get('surname', 'Не указана')}\nВаша организация: {data.get('organization', 'Не указана')}\nВаш номер телефона: {data.get('phone', 'Не указан')}\n\nПри необходимости просьба обратиться в поддержку!")
    else:
        await message.answer('Обратитесь в поддержку')