from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv, find_dotenv
import os
import asyncio

from src.bot.handlers.user import user_router
from src.bot.handlers.admin import admin_router
from src.bot.middlewares.language_middleware import LanguageMiddleware
from src.scraper.parser import start_parsing_loop

load_dotenv(find_dotenv())

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher(storage=MemoryStorage())

dp.message.middleware(LanguageMiddleware())
dp.callback_query.middleware(LanguageMiddleware())

dp.include_router(user_router)
dp.include_router(admin_router)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)

    asyncio.create_task(start_parsing_loop(bot))

    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot Stopped")
