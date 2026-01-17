from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from src.db.session import Local_Session
from src.db.crud.user_crud import get_user

class IsAdmin(BaseFilter):
    async def __call__(self, events: Message | CallbackQuery) -> bool:
        user_id = events.from_user.id
        async with Local_Session() as session:
            user = await get_user(session, user_id)
            return user and user.role == "admin"
