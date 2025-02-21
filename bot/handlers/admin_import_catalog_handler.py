from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from filters.chat_types import ChatTypeFilter, IsAdmin
from fsm.catalog_fsm import AddCatalogForm
from aiogram.filters import StateFilter

from keyboards.inline.admin_keyboard import create_simple_inline_navigation
from config import CATALOG_FILE_PATH


router = Router(name="admin_import_catalog")
router.message.filter(ChatTypeFilter(["private"]), IsAdmin())


@router.message(F.text == "➕Изменить каталог")
async def admin_import_catalog(message: types.Message, state: FSMContext):
    await message.answer(
        AddCatalogForm.text.get("AddCatalogForm.new_catalog"),
        reply_markup=create_simple_inline_navigation(),
    )

    await state.set_state(AddCatalogForm.new_catalog)


@router.message(
    F.content_type.in_({"document"}), StateFilter(AddCatalogForm.new_catalog)
)
async def admin_import_new_catalog(message: types.Message, state: FSMContext, bot: Bot):
    try:
        if not message.content_type == "document":
            await message.answer(
                "Отправьте файл для обновления!",
                reply_markup=create_simple_inline_navigation(),
            )
            return

        file_id = message.document.file_id

        if not file_id:
            await message.answer(
                "Ошибка со стороны телеграмма попробуйте снова.",
                reply_markup=create_simple_inline_navigation(),
            )
            return

        file = await bot.get_file(file_id)
        if message.document.file_name != "data.xlsx":
            await message.answer("Не правильный формат файла, пример - 'data.xlsx'")
            return

        await bot.download_file(file.file_path, CATALOG_FILE_PATH)

        await message.answer(
            "Файл каталога успешно обновлен, нажмите обновить каталог чтобы добавить новые товары!"
        )
        await state.clear()
    except Exception as e:
        await message.answer(
            f"Произошла ошибка {e} \n Нажмите заново кнопку добавления и отправьте ваш файл"
        )
        await state.clear()
