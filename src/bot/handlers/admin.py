from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from src.bot.filters.admin_filter import IsAdmin
import asyncio

from src.db.session import Local_Session
from src.db.crud.user_crud import get_user, update_user
from src.db.models import User
from src.bot.keyboards.admin_kb import get_admin_keyboard
from sqlalchemy import select

admin_router = Router()
admin_router.message.filter(IsAdmin())

texts = {
    "ru": {
        "not_admin": "У вас нет прав администратора.",
        "users_list": "Список пользователей:",
        "sub_granted": "Подписка выдана пользователю {user_id}.",
        "sub_revoked": "Подписка отозвана у пользователя {user_id}.",
        "broadcast": "Рассылка: {message}"
    },
    "az": {
        "not_admin": "Admin hüquqlarınız yoxdur.",
        "users_list": "İstifadəçilər siyahısı:",
        "sub_granted": "Abunəlik {user_id} istifadəçisinə verildi.",
        "sub_revoked": "Abunəlik {user_id} istifadəçisindən alındı.",
        "broadcast": "Yayım: {message}"
    }
}

@admin_router.message(Command("admin"))
async def cmd_admin(message: Message):
    user_id = message.from_user.id
    async with Local_Session() as session:
        user = await get_user(session, user_id)
        if user.role != "admin":
            lang = user.language if user else "ru"
            await message.reply(texts[lang]["not_admin"])
            return
        lang = user.language
    keyboard = get_admin_keyboard(lang)
    await message.reply("Админ панель", reply_markup=keyboard)

@admin_router.message(F.text == "Просмотр пользователей")
async def list_users_ru(message: Message):
    user_id = message.from_user.id
    async with Local_Session() as session:
        user = await get_user(session, user_id)
        if user.role != "admin":
            await message.reply(texts["ru"]["not_admin"])
            return
        result = await session.execute(select(User))
        users = result.scalars().all()
        text = "Список пользователей:\n"
        for u in users:
            text += f"ID: {u.id}, Роль: {u.role}, Подписка: {u.subscription}, Язык: {u.language}\n"
    await message.reply(text)

@admin_router.message(F.text == "İstifadəçiləri göstər")
async def list_users_az(message: Message):
    await list_users_ru(message)

@admin_router.message(F.text == "Управление подписками")
async def manage_subs_ru(message: Message):
    await message.reply("Функция в разработке. Используйте /grant_sub <user_id> или /revoke_sub <user_id>")

@admin_router.message(Command("grant_sub"))
async def grant_sub(message: Message):
    user_id = message.from_user.id
    args = message.text.split()
    if len(args) < 2:
        await message.reply("Использование: /grant_sub <user_id>")
        return
    target_id = int(args[1])
    async with Local_Session() as session:
        admin = await get_user(session, user_id)
        if admin.role != "admin":
            await message.reply(texts["ru"]["not_admin"])
            return
        await update_user(session, target_id, subscription=True)
    await message.reply(texts["ru"]["sub_granted"].format(user_id=target_id))

@admin_router.message(Command("revoke_sub"))
async def revoke_sub(message: Message):
    user_id = message.from_user.id
    args = message.text.split()
    if len(args) < 2:
        await message.reply("Использование: /revoke_sub <user_id>")
        return
    target_id = int(args[1])
    async with Local_Session() as session:
        admin = await get_user(session, user_id)
        if admin.role != "admin":
            await message.reply(texts["ru"]["not_admin"])
            return
        from sqlalchemy import select
        from src.db.models.searchfilter import SearchFilter
        result = await session.execute(select(SearchFilter).where(SearchFilter.user_id == target_id))
        filters = result.scalars().all()
        for f in filters:
            await session.delete(f)
        from src.db.session import Local_Session as LS
        async with LS() as sess:
            await update_user(sess, target_id, subscription=False)
    await message.reply(texts["ru"]["sub_revoked"].format(user_id=target_id))

@admin_router.message(F.text == "Рассылка сообщений")
async def broadcast_ru(message: Message):
    await message.reply("Используйте команду /broadcast <сообщение> для рассылки подписчикам.")


@admin_router.message(Command("broadcast"))
async def cmd_broadcast(message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("Использование: /broadcast <сообщение>")
        return
    text = args[1]

    user_id = message.from_user.id
    async with Local_Session() as session:
        admin = await get_user(session, user_id)
        if not admin or admin.role != "admin":
            lang = admin.language if admin else "ru"
            await message.reply(texts[lang]["not_admin"])
            return

        result = await session.execute(select(User).where(User.subscription == True))
        users = result.scalars().all()

    sent = 0
    failed = 0
    for u in users:
        try:
            await message.bot.send_message(u.id, text, disable_notification=True)
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)

    await message.reply(f"Рассылка завершена. Отправлено: {sent}, Ошибок: {failed}")
