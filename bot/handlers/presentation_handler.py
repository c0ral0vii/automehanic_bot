from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import os

presentation_router = Router(name="presentations")

PDF_FOLDER = 'bot/utils/data/presentations'

@presentation_router.message(StateFilter(None), F.text == '📑 Презентации по продукту')
async def send_presentations(message: types.Message):
    pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.endswith('.pdf')]

    buttons = [[InlineKeyboardButton(text=pdf, callback_data=pdf)] for pdf in pdf_files]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer("Выберите презентацию:", reply_markup=keyboard)


@presentation_router.callback_query(F.data.endswith('.pdf'))
async def send_pdf(call: types.CallbackQuery):
    pdf_path = os.path.join(PDF_FOLDER, call.data)

    if os.path.exists(pdf_path):
        await call.message.answer_document(document=types.FSInputFile(pdf_path))
        await call.answer()
    else:
        await call.message.answer("Файл не найден.")
        await call.answer()
