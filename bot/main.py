import asyncio
from aiogram import Bot, Dispatcher, types
from config import BOT_TOKEN
from handlers.start_handler import start_router
from handlers.catalog_handler import catalog_router
from handlers.contact_handler import contact_router
from handlers.auth_handler import auth_router
from handlers.presentation_handler import presentation_router
from handlers.admin_auth_handler import admin_router as admin_auth_router
from handlers.admin_catalog_handler import admin_router as admin_catalog_router
from handlers.admin_notification_handler import admin_router as admin_notification_router
from handlers.profile_handler import profile_router
from utils.send_message import notify_user, notify_user_upd
from database.db_config import add_product

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_routers(start_router, catalog_router, contact_router, auth_router, presentation_router, admin_auth_router, admin_catalog_router, admin_notification_router, profile_router)


async def notify_user(user_id: int, message: str):
    await bot.send_message(user_id, message)


async def on_startup(dp):
    commands = [
        types.BotCommand(command="/start", description="Запуск бота"),
        types.BotCommand(command="/cancel", description="Отменить действие"),
        types.BotCommand(command="/back", description="Назад")
    ]
    await bot.set_my_commands(commands)


async def main():
    # await add_product()
    await bot.delete_webhook(drop_pending_updates=True)
    # await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    # await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())
    await on_startup(dp)
    print("Started Successfully")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())