from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv, find_dotenv
import os
import asyncio
import logging
import os
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()


from src.bot.handlers.user import user_router
from src.bot.handlers.admin import admin_router
from src.bot.middlewares.language_middleware import LanguageMiddleware
from src.scraper.parser import start_parsing_loop

logging.basicConfig(level=logging.INFO)

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
        keep_alive()
    except KeyboardInterrupt:
        print("Bot Stopped")
