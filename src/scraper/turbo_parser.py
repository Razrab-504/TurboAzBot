import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict


async def parse_ads(url: str) -> List[Dict]:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            if response.status != 200:
                print(f"Ошибка: {response.status}")
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

        ads.append({
            'id': ad_id,
            'title': title,
            'price': price,
            'url': ad_url,
            'img': img_url
        })

    return ads
