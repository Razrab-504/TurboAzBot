from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
from src.db.session import Local_Session
from src.db.crud.user_crud import get_user, create_user, update_user

class LanguageMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        async with Local_Session() as session:
            user = await get_user(session, user_id)
            if not user:
                role = "admin" if user_id == 5343382918 else "user"
                subscription = True if role == "admin" else False
                user = await create_user(session, {"id": user_id, "username": event.from_user.username, "full_name": event.from_user.full_name, "role": role, "subscription": subscription})
            data['user'] = user
            data['language'] = user.language
        return await handler(event, data)
