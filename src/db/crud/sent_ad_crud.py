from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.db.models.sent_ad import SentAd


async def create_sent_ad(session: AsyncSession, user_id: int, ad_id: str) -> SentAd:
    sent_ad = SentAd(user_id=user_id, ad_id=ad_id)
    session.add(sent_ad)
    await session.commit()
    await session.refresh(sent_ad)
    return sent_ad


async def is_ad_sent_to_user(session: AsyncSession, user_id: int, ad_id: str) -> bool:
    q = select(SentAd).where(SentAd.user_id == user_id, SentAd.ad_id == ad_id)
    result = await session.execute(q)
    return result.scalars().first() is not None
