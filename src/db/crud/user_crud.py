from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models.users import User

async def get_user(session: AsyncSession, user_id: int) -> User | None:
    return await session.get(User, user_id)

async def create_user(session: AsyncSession, user_data: dict) -> User:
    user = User(**user_data)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

async def update_user(session: AsyncSession, user_id: int, **kwargs) -> User | None:
    user = await session.get(User, user_id)
    if user:
        for key, value in kwargs.items():
            setattr(user, key, value)
        await session.commit()
        await session.refresh(user)
    return user
