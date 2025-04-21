from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import os

presentation_router = Router(name="presentations")

PDF_FOLDER = "./bot/utils/data/presentations"


@presentation_router.message(F.text == "📑 Презентации по продукту")
async def send_presentations(message: types.Message):
    try:
        pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")]

        buttons = [
            [InlineKeyboardButton(text=pdf, callback_data=pdf.replace(" ", "_"))]
            for pdf in pdf_files
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

        await message.answer("Выберите презентацию:", reply_markup=keyboard)
    except Exception as e:
        await message.answer(
            f"Не удалось отправить презентации, повторите попытку, отправьте это разработчику {e}"
        )


@presentation_router.callback_query(F.data.endswith(".pdf"))
async def send_pdf(call: types.CallbackQuery):
    pdf_path = os.path.join(PDF_FOLDER, call.data.replace("_", " "))

    if os.path.exists(pdf_path):
        await call.message.answer_document(document=types.FSInputFile(pdf_path))
        await call.answer("Приятного ознакомленя!")
    else:
        await call.message.answer("Файл не найден.")
        await call.answer("Ошибка")
