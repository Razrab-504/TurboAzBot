import asyncio
import aiohttp
import random
import logging
from bs4 import BeautifulSoup

from src.db.session import Local_Session
from src.db.crud.advertisement_crud import get_ad_by_id, create_ad
from src.db.crud.sent_ad_crud import is_ad_sent_to_user, create_sent_ad
from src.db.crud.user_crud import update_user
from src.db.models import User
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from aiogram import Bot
import datetime

async def parse_page(url: str) -> list:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            if response.status != 200:
                print(f"Ошибка парсинга {url}: {response.status}")
                return []
            html = await response.text(encoding='utf-8')

    soup = BeautifulSoup(html, 'html.parser')
    ads = []
    cards = soup.find_all('div', class_='products-i')

    for card in cards:
        link_tag = card.find('a', class_='products-i__link')
        if not link_tag:
            continue

        ad_url = 'https://turbo.az' + link_tag['href']
        ad_id = ad_url.split('/')[-1].split('?')[0]

        title_tag = card.find('div', class_='products-i__name')
        title = title_tag.text.strip() if title_tag else 'Без названия'

        price_tag = card.find('div', class_='product-price')
        price = price_tag.text.strip() if price_tag else 'Цена не указана'

        img_tag = card.find('img', class_='products-i__photo')
        img_url = img_tag['data-src'] if img_tag and 'data-src' in img_tag.attrs else (img_tag['src'] if img_tag else '')

        datetime_tag = card.find('div', class_='products-i__datetime')
        datetime_str = datetime_tag.text.strip() if datetime_tag else ''

        ads.append({
            'id': ad_id,
            'title': title,
            'price': price,
            'url': ad_url,
            'img': img_url,
            'city': datetime_str.split(',')[0] if ',' in datetime_str else '',
            'published_at': datetime_str.split(',')[1].strip() if ',' in datetime_str else datetime_str
        })

    return ads

async def notify_admins(bot: Bot, message: str):
    async with Local_Session() as session:
        result = await session.execute(select(User).where(User.role == "admin"))
        admins = result.scalars().all()
        for admin in admins:
            try:
                await bot.send_message(admin.id, f"⚠️ {message}")
            except Exception:
                pass

async def check_expired_subscriptions():
    async with Local_Session() as session:
        now = datetime.datetime.utcnow()
        result = await session.execute(select(User).where(User.subscription == True).where(User.expiry_date.isnot(None)).where(User.expiry_date < now))
        expired_users = result.scalars().all()
        for user in expired_users:
            await update_user(session, user.id, subscription=False)
            logging.info(f"Подписка истекла для пользователя {user.id}")

async def parse_user_filters(bot: Bot):
    await check_expired_subscriptions()
    async with Local_Session() as session:
        result = await session.execute(select(User).options(joinedload(User.filters)).where(User.subscription == True))
        users = result.scalars().unique().all()

        for user in users:
            for filter_ in user.filters:
                url = filter_.query_url
                try:
                    ads = await parse_page(url)
                except Exception as e:
                    logging.error(f"Ошибка парсинга для фильтра {filter_.id}: {e}")
                    await notify_admins(bot, f"Ошибка парсинга фильтра {filter_.id}: {str(e)}")
                    continue
                delay = random.uniform(3, 7)
                await asyncio.sleep(delay)

                parts = filter_.label.split()
                make = parts[0].lower() if len(parts) > 0 else ''
                model = " ".join(parts[1:-1]).lower() if len(parts) > 2 else (parts[1].lower() if len(parts) > 1 else '')

                for ad in ads:
                    title_lower = ad['title'].lower()
                    if make and make not in title_lower:
                        continue
                    if model and model not in title_lower:
                        continue

                    existing = await get_ad_by_id(session, ad['id'])
                    if not existing:
                        await create_ad(session, ad)

                    sent = await is_ad_sent_to_user(session, user.id, ad['id'])
                    if not sent:
                        city = ad.get('city', '')
                        pub = ad.get('published_at', '')
                        location = f"📍 {city}" if city else ""
                        time_info = f"⏰ {pub}" if pub else ""
                        caption = f"<b>{ad['title']}</b>\n\n💰 {ad['price']}\n{location}\n{time_info}\n🔗 {ad['url']}"
                        try:
                            await bot.send_photo(
                                chat_id=user.id,
                                photo=ad['img'],
                                caption=caption,
                                parse_mode='HTML'
                            )
                        except Exception as e:
                            await bot.send_message(
                                chat_id=user.id,
                                text=caption,
                                parse_mode='HTML'
                            )
                        await create_sent_ad(session, user.id, ad['id'])
                        print(f"Отправлено пользователю {user.id}: {ad['id']}")

async def start_parsing_loop(bot: Bot):
    while True:
        await parse_user_filters(bot)
        delay = random.uniform(300, 600)
        await asyncio.sleep(delay)