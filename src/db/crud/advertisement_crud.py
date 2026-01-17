from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models.advertisement import Advertisement


async def get_ad_by_id(session: AsyncSession, ad_id: str) -> Advertisement | None:
    return await session.get(Advertisement, ad_id)


async def create_ad(session: AsyncSession, ad_data: dict) -> Advertisement:
    ad = Advertisement(
        id=ad_data['id'],
        title=ad_data['title'],
        price=ad_data['price'],
        url=ad_data['url'],
        city=ad_data.get('city'),
        published_at=ad_data.get('published_at'),
        last_price=ad_data['price']
    )
    session.add(ad)
    await session.commit()
    await session.refresh(ad)
    return ad
