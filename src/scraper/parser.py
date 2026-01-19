import asyncio
import aiohttp
import random
import logging
from bs4 import BeautifulSoup
import pyppeteer
from pyppeteer import launch
from pyppeteer_stealth import stealth

from src.db.session import Local_Session

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]
from src.db.crud.advertisement_crud import get_ad_by_id, create_ad
from src.db.crud.sent_ad_crud import is_ad_sent_to_user, create_sent_ad
from src.db.crud.user_crud import update_user
from src.db.models import User
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from aiogram import Bot
import datetime

async def parse_page(url: str) -> list:
    browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
    page = await browser.newPage()
    await stealth(page)
    await page.setUserAgent(random.choice(USER_AGENTS))
    await page.setExtraHTTPHeaders({
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8,az;q=0.7',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
    })
    try:
        await page.goto(url, {'waitUntil': 'networkidle2', 'timeout': 30000})
        html = await page.content()
        print(f"HTML preview: {html[:500]}")
    except Exception as e:
        print(f"Ошибка парсинга {url}: {e}")
        await browser.close()
        return []
    finally:
        await browser.close()

    soup = BeautifulSoup(html, 'html.parser')
    ads = []
    cards = soup.find_all('div', class_='products-i')
    print(f"Парсинг {url}: найдено {len(cards)} карточек")

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
            except Exception as e:
                logging.error(f"Не удалось отправить уведомление админу {admin.id}: {e}")

async def check_expired_subscriptions():
    async with Local_Session() as session:
        now = datetime.datetime.utcnow()
        result = await session.execute(select(User).where(User.subscription == True).where(User.expiry_date.isnot(None)).where(User.expiry_date < now))
        expired_users = result.scalars().all()
        for user in expired_users:
            await update_user(session, user.id, subscription=False)
            logging.info(f"Подписка истекла для пользователя {user.id}")

async def parse_user_filters(bot: Bot):
    print("Запуск парсинга фильтров")
    await check_expired_subscriptions()

    async with Local_Session() as session:
        result = await session.execute(select(User).options(joinedload(User.filters)).where(User.subscription == True))
        users = result.scalars().unique().all()
        print(f"Найдено {len(users)} пользователей с подпиской")

        url_to_users = {}
        for user in users:
            for filter_ in user.filters:
                if filter_.query_url not in url_to_users:
                    url_to_users[filter_.query_url] = []
                url_to_users[filter_.query_url].append((user.id, filter_))

        print(f"Парсинг {len(url_to_users)} уникальных URL")

        for url, user_filters in url_to_users.items():
            try:
                ads = await parse_page(url)
                print(f"Для URL найдено {len(ads)} объявлений")
            except Exception as e:
                logging.error(f"Ошибка парсинга {url}: {e}")
                await notify_admins(bot, f"Ошибка парсинга: {str(e)}")
                continue

            for user_id, filter_ in user_filters:
                parts = filter_.label.split()
                make = parts[0].lower() if len(parts) > 0 else ''
                model = " ".join(parts[1:-1]).lower() if len(parts) > 2 else (parts[1].lower() if len(parts) > 1 else '')

                filtered_ads = []
                for ad in ads:
                    title_lower = ad['title'].lower()
                    if make and make not in title_lower:
                        continue
                    if model and model not in title_lower:
                        continue
                    filtered_ads.append(ad)

                print(f"Для пользователя {user_id} фильтр '{filter_.label}' прошел {len(filtered_ads)} объявлений")

                for ad in filtered_ads:
                    existing = await get_ad_by_id(session, ad['id'])
                    if not existing:
                        await create_ad(session, ad)

                    sent = await is_ad_sent_to_user(session, user_id, ad['id'])
                    if not sent:
                        city = ad.get('city', '')
                        pub = ad.get('published_at', '')
                        location = f"📍 {city}" if city else ""
                        time_info = f"⏰ {pub}" if pub else ""
                        caption = f"<b>{ad['title']}</b>\n\n💰 {ad['price']}\n{location}\n{time_info}\n🔗 {ad['url']}"
                        try:
                            await bot.send_photo(
                                chat_id=user_id,
                                photo=ad['img'],
                                caption=caption,
                                parse_mode='HTML'
                            )
                            print(f"Отправлено фото пользователю {user_id}")
                        except Exception as e:
                            try:
                                await bot.send_message(
                                    chat_id=user_id,
                                    text=caption,
                                    parse_mode='HTML'
                                )
                                print(f"Отправлено сообщение пользователю {user_id}")
                            except Exception as e2:
                                print(f"Ошибка отправки пользователю {user_id}: {e2}")
                        await create_sent_ad(session, user_id, ad['id'])
                        print(f"Отправлено пользователю {user_id}: {ad['id']}")

            delay = random.uniform(3, 7)
            await asyncio.sleep(delay)

async def start_parsing_loop(bot: Bot):
    while True:
        await parse_user_filters(bot)
        delay = random.uniform(60, 120)  # уменьшил для тестирования
        print(f"Ожидание {delay} секунд до следующего парсинга")
        await asyncio.sleep(delay)