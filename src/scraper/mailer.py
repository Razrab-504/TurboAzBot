import asyncio
from aiogram import Bot
from urllib.parse import urlparse, parse_qs

from src.db.session import Local_Session
from src.db.crud.sent_ad_crud import is_ad_sent_to_user, create_sent_ad
from src.db.models import Advertisement, User, SearchFilter
from sqlalchemy import select
from sqlalchemy.orm import joinedload

async def send_new_ads(bot: Bot):
    async with Local_Session() as session:
        result = await session.execute(select(User).options(joinedload(User.filters)).where(User.subscription == True))
        users = result.scalars().unique().all()

        for user in users:
            filters = user.filters
            for filter_ in filters:
                parsed = urlparse(filter_.query_url)
                params = parse_qs(parsed.query)

                make = params.get('q[make][]', [''])[0].lower()
                model = params.get('q[model][]', [''])[0].lower()
                min_price = int(params.get('q[price_from]', [0])[0] or 0)
                max_price = int(params.get('q[price_to]', [99999999])[0] or 99999999)

                result = await session.execute(select(Advertisement))
                ads = result.scalars().all()

                for ad in ads:
                    if make and make not in ad.title.lower():
                        continue
                    if model and model not in ad.title.lower():
                        continue
                    try:
                        ad_price = int(''.join(filter(str.isdigit, ad.price)))
                        if not (min_price <= ad_price <= max_price):
                            continue
                    except:
                        continue

                    sent = await is_ad_sent_to_user(session, user.id, ad.id)
                    if not sent:
                        try:
                            await bot.send_photo(
                                chat_id=user.id,
                                photo=ad.img,
                                caption=f"<b>{ad.title}</b>\n\n💰 {ad.price}\n🔗 {ad.url}",
                                parse_mode='HTML'
                            )
                        except Exception as e:
                            await bot.send_message(
                                chat_id=user.id,
                                text=f"<b>{ad.title}</b>\n\n💰 {ad.price}\n🔗 {ad.url}",
                                parse_mode='HTML'
                            )
                        await create_sent_ad(session, user.id, ad.id)

async def start_mailing_loop(bot: Bot):
    while True:
        await send_new_ads(bot)
        await asyncio.sleep(30)
