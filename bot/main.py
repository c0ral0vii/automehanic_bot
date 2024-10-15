import asyncio
from aiogram import Bot, Dispatcher, types
from config import BOT_TOKEN
from handlers.start_handler import start_router
from handlers.catalog_handler import catalog_router
from utils.bot_commands import private


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_routers(start_router, catalog_router)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    print("Started Successfully")
    await dp.start_polling(bot)

asyncio.run(main())