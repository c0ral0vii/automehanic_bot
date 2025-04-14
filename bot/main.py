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
from handlers.admin_notification_handler import (
    admin_router as admin_notification_router,
)
from handlers.profile_handler import profile_router
from handlers.undefiend_handler import undefiend_handler
from handlers.admin_import_catalog_handler import router
from service.count_updater.service import UpdateCountService
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


dp.include_routers(
    start_router,
    catalog_router,
    contact_router,
    auth_router,
    presentation_router,
    admin_auth_router,
    admin_catalog_router,
    admin_notification_router,
    profile_router,
    router,
    undefiend_handler,
)


async def on_startup(dp):
    commands = [
        types.BotCommand(command="/start", description="Запуск бота"),
        types.BotCommand(command="/cancel", description="Отменить действие"),
        types.BotCommand(command="/back", description="Назад"),
    ]
    await bot.set_my_commands(commands)


async def main():
    await run_updater()

    await bot.delete_webhook(drop_pending_updates=True)
    await on_startup(dp)
    print("Start")
    await dp.start_polling(bot)

async def run_updater():
    updater = UpdateCountService()

    scheduler = AsyncIOScheduler(timezone=pytz.timezone("Europe/Moscow"))
    await updater.check_stock()
    scheduler.add_job(updater.check_stock, 'cron', hour=0, minute=0)

    scheduler.start()

if __name__ == "__main__":
    asyncio.run(main())
