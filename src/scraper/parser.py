import asyncio
import random
import logging
from bs4 import BeautifulSoup
import ssl
import certifi
import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import quote

from src.db.session import Local_Session

from src.db.crud.advertisement_crud import get_ad_by_id, create_ad
from src.db.crud.sent_ad_crud import is_ad_sent_to_user, create_sent_ad
from src.db.crud.user_crud import update_user
from src.db.models import User
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from aiogram import Bot
import datetime
import os

async def parse_page(url: str, max_retries: int = 3) -> list:
    api_key = os.getenv("SCRAPING_API_KEY")
    if not api_key:
        logging.error("SCRAPING_API_KEY not set")
        return []

    for attempt in range(max_retries):
        try:
            scraping_url = f"https://api.scrapingapi.com/scrape?api_key={api_key}&url={quote(url)}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            logging.info(f"Попытка {attempt + 1}: Парсинг URL длиной {len(url)} символов")
            
            response = requests.get(
                scraping_url,
                headers=headers,
                timeout=90,
                verify=False
            )

            logging.info(f"Статус ответа: {response.status_code}")

            if response.status_code == 400:
                error_text = response.text[:300]
                logging.error(f"Ошибка 400 - некорректный URL или параметры")
                logging.error(f"URL: {url}")
                logging.error(f"Ответ API: {error_text}")
                return []

            if response.status_code == 403:
                logging.error("Ошибка 403 - проверьте API ключ или баланс")
                return []

            if response.status_code == 429:
                logging.error("Ошибка 429 - превышен лимит запросов")
                if attempt < max_retries - 1:
                    await asyncio.sleep(random.uniform(30, 60))
                    continue
                return []

            if response.status_code != 200:
                error_text = response.text[:300]
                logging.error(f"Ошибка {response.status_code}: {error_text}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(random.uniform(5, 10))
                    continue
                return []

            html = response.text

            if len(html) < 500:
                logging.warning(f"Слишком короткий ответ: {len(html)} байт")
                if attempt < max_retries - 1:
                    await asyncio.sleep(random.uniform(5, 10))
                    continue
                return []

            soup = BeautifulSoup(html, 'lxml')
            ads = []
            cards = soup.find_all('div', class_='products-i')
            
            logging.info(f"Найдено {len(cards)} карточек объявлений")

            for card in cards:
                try:
                    link_tag = card.find('a', class_='products-i__link')
                    if not link_tag or 'href' not in link_tag.attrs:
                        continue

                    ad_url = 'https://turbo.az' + link_tag['href']
                    ad_id = ad_url.split('/')[-1].split('?')[0]

                    title_tag = card.find('div', class_='products-i__name')
                    title = title_tag.text.strip() if title_tag else 'Без названия'

                    price_tag = card.find('div', class_='product-price')
                    price = price_tag.text.strip() if price_tag else 'Цена не указана'

                    img_tag = card.find('img', class_='products-i__photo')
                    img_url = ''
                    if img_tag:
                        img_url = img_tag.get('data-src') or img_tag.get('src', '')

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
                except Exception as e:
                    logging.warning(f"Ошибка парсинга карточки: {e}")
                    continue

            logging.info(f"Успешно спарсено {len(ads)} объявлений")
            return ads
            
        except requests.exceptions.Timeout:
            logging.error(f"Timeout на попытке {attempt + 1}")
            if attempt < max_retries - 1:
                await asyncio.sleep(random.uniform(10, 15))
                continue
            return []
            
        except Exception as e:
            logging.error(f"Критическая ошибка (попытка {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(random.uniform(5, 10))
                continue
            return []
    
    return []

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
        result = await session.execute(
            select(User)
            .where(User.subscription == True)
            .where(User.expiry_date.isnot(None))
            .where(User.expiry_date < now)
        )
        expired_users = result.scalars().all()
        for user in expired_users:
            await update_user(session, user.id, subscription=False)
            logging.info(f"Подписка истекла для пользователя {user.id}")

async def parse_user_filters(bot: Bot):
    logging.info("Запуск парсинга фильтров")
    await check_expired_subscriptions()

    async with Local_Session() as session:
        result = await session.execute(
            select(User)
            .options(joinedload(User.filters))
            .where(User.subscription == True)
        )
        users = result.scalars().unique().all()
        logging.info(f"Найдено {len(users)} пользователей с подпиской")

        url_to_users = {}
        for user in users:
            for filter_ in user.filters:
                if filter_.query_url not in url_to_users:
                    url_to_users[filter_.query_url] = []
                url_to_users[filter_.query_url].append((user.id, filter_))

        logging.info(f"Парсинг {len(url_to_users)} уникальных URL")

        for url, user_filters in url_to_users.items():
            try:
                ads = await parse_page(url)
                logging.info(f"Для URL найдено {len(ads)} объявлений")
                
                if len(ads) == 0:
                    logging.warning(f"Не найдено объявлений для URL: {url}")
                    
            except Exception as e:
                logging.error(f"Ошибка парсинга {url}: {e}")
                await notify_admins(bot, f"Ошибка парсинга: {str(e)[:100]}")
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

                logging.info(f"Для пользователя {user_id} фильтр '{filter_.label}' прошел {len(filtered_ads)} объявлений")

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
                            if ad.get('img'):
                                await bot.send_photo(
                                    chat_id=user_id,
                                    photo=ad['img'],
                                    caption=caption,
                                    parse_mode='HTML'
                                )
                            else:
                                await bot.send_message(
                                    chat_id=user_id,
                                    text=caption,
                                    parse_mode='HTML'
                                )
                            logging.info(f"Отправлено объявление {ad['id']} пользователю {user_id}")
                        except Exception as e:
                            logging.error(f"Ошибка отправки пользователю {user_id}: {e}")
                            try:
                                await bot.send_message(
                                    chat_id=user_id,
                                    text=caption,
                                    parse_mode='HTML'
                                )
                            except Exception as e2:
                                logging.error(f"Повторная ошибка отправки пользователю {user_id}: {e2}")
                        
                        await create_sent_ad(session, user_id, ad['id'])

            delay = random.uniform(10, 20)
            await asyncio.sleep(delay)

async def start_parsing_loop(bot: Bot):
    """Основной цикл парсинга"""
    while True:
        try:
            await parse_user_filters(bot)
        except Exception as e:
            logging.error(f"Критическая ошибка в цикле парсинга: {e}")
            await notify_admins(bot, f"Критическая ошибка: {str(e)[:100]}")
        
        delay = random.uniform(120, 180)  # 2-3 минуты между циклами
        logging.info(f"Ожидание {delay:.0f} секунд до следующего парсинга")
        await asyncio.sleep(delay)