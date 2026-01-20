from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.db.models.searchfilter import SearchFilter


async def get_user_filters(session: AsyncSession, user_id: int) -> list[SearchFilter]:
    result = await session.execute(select(SearchFilter).where(SearchFilter.user_id == user_id))
    return result.scalars().all()


async def delete_filter(session: AsyncSession, filter_id: int) -> bool:
    filter_obj = await session.get(SearchFilter, filter_id)
    if filter_obj:
        await session.delete(filter_obj)
        await session.commit()
        return True
    return False
