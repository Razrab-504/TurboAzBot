import asyncio
import aiohttp
import random
import logging
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
# from playwright_stealth import stealth

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
import os

async def parse_page(url: str, max_retries: int = 3) -> list:
    """Парсинг страницы с обходом Cloudflare и повторными попытками"""
    
    for attempt in range(max_retries):
        try:
            proxy_list = os.getenv("PROXY_LIST", "").split(",") if os.getenv("PROXY_LIST") else []
            proxy = None
            if proxy_list:
                proxy_str = random.choice(proxy_list).strip()
                if proxy_str:
                    proxy = {"server": proxy_str}

            async with async_playwright() as p:
                # Запуск браузера с дополнительными аргументами
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--disable-accelerated-2d-canvas',
                        '--disable-gpu',
                        '--window-size=1920,1080',
                    ],
                    proxy=proxy
                )
                
                # Создание контекста с реалистичными параметрами
                context = await browser.new_context(
                    user_agent=random.choice(USER_AGENTS),
                    viewport={'width': 1920, 'height': 1080},
                    locale='ru-RU',
                    timezone_id='Asia/Baku',
                    extra_http_headers={
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Cache-Control': 'max-age=0',
                    }
                )
                
                page = await context.new_page()
                
                # Применяем stealth для обхода детекции
                # await stealth(page)
                
                # Добавляем JavaScript для маскировки автоматизации
                await page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['ru-RU', 'ru', 'en-US', 'en']
                    });
                    window.chrome = {
                        runtime: {}
                    };
                """)
                
                try:
                    # Переход на страницу с увеличенным таймаутом
                    await page.goto(url, wait_until='domcontentloaded', timeout=90000)
                    
                    # Ждем загрузки контента (не Cloudflare страницы)
                    await page.wait_for_selector('.products-i', timeout=60000)
                    
                    # Дополнительная задержка для полной загрузки
                    await asyncio.sleep(random.uniform(2, 4))
                    
                    html = await page.content()
                    
                    # Проверяем, не Cloudflare ли это
                    if "Just a moment" in html or "Checking your browser" in html:
                        logging.warning(f"Cloudflare challenge detected on attempt {attempt + 1}")
                        await browser.close()
                        if attempt < max_retries - 1:
                            await asyncio.sleep(random.uniform(5, 10))
                            continue
                        else:
                            return []
                    
                    logging.info(f"Успешно загружена страница: {url}")
                    
                except Exception as e:
                    logging.error(f"Ошибка при загрузке страницы (попытка {attempt + 1}): {e}")
                    await browser.close()
                    if attempt < max_retries - 1:
                        await asyncio.sleep(random.uniform(3, 7))
                        continue
                    else:
                        return []
                finally:
                    await browser.close()

            # Парсинг HTML
            soup = BeautifulSoup(html, 'html.parser')
            ads = []
            cards = soup.find_all('div', class_='products-i')
            logging.info(f"Парсинг {url}: найдено {len(cards)} карточек")

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
                img_url = img_tag.get('data-src') or img_tag.get('src', '') if img_tag else ''

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
            
        except Exception as e:
            logging.error(f"Критическая ошибка парсинга (попытка {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(random.uniform(5, 10))
                continue
            else:
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

            # Задержка между URL
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