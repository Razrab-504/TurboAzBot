from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import Local_Session
from src.db.models.searchfilter import SearchFilter
from src.scraper.turbo_parser import parse_ads
from src.db.crud.advertisement_crud import get_ad_by_id, create_ad


async def scrape_and_send(bot: Bot, filter_: SearchFilter):
    url = filter_.query_url
    ads = await parse_ads(url)

    async with Local_Session() as session:
        for ad in ads:
            existing = await get_ad_by_id(session, ad['id'])
            if not existing:
                await create_ad(session, ad)
                try:
                    await bot.send_photo(
                        chat_id=filter_.user_id,
                        photo=ad['img'],
                        caption=f"<b>{ad['title']}</b>\n\n💰 Цена: {ad['price']}\n🔗 {ad['url']}",
                        parse_mode='HTML'
                    )
                except Exception as e:
                    print(f"Ошибка отправки: {e}")
                    await bot.send_message(
                        chat_id=filter_.user_id,
                        text=f"<b>{ad['title']}</b>\n\n💰 Цена: {ad['price']}\n🔗 {ad['url']}",
                        parse_mode='HTML'
                    )
