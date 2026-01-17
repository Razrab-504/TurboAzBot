from src.db.base import Base
from src.db.session import engine
import asyncio

from src.db.models import Advertisement, SearchFilter, User, SentAd


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        

asyncio.run(create_tables())
