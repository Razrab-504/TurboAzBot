from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv, find_dotenv
import os
import asyncio
import logging
from aiohttp import web

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

async def handle_webhook(request):
    data = await request.json()
    update = await dp.feed_webhook_update(bot, data)
    return web.Response(text="OK")

async def handle_ping(request):
    return web.Response(text="I am alive! Bot is running.")

async def start_web_server():
    app = web.Application()
    app.router.add_post('/webhook', handle_webhook)
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"Web server started on port {port}")

    webhook_url = os.getenv("WEBHOOK_URL")
    if webhook_url:
        await bot.set_webhook(webhook_url + "/webhook")
        logging.info(f"Webhook set to {webhook_url}/webhook")
    else:
        await bot.delete_webhook()
        logging.info("Using polling")

async def main():
    asyncio.create_task(start_parsing_loop(bot))

    asyncio.create_task(start_web_server())

    if not os.getenv("WEBHOOK_URL"):
        await dp.start_polling(bot)
    else:
        while True:
            await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot Stopped")