from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_admin_keyboard(language: str) -> ReplyKeyboardMarkup:
    if language == "ru":
        buttons = [
            [KeyboardButton(text="Управление подписками")],
            [KeyboardButton(text="Просмотр пользователей")],
            [KeyboardButton(text="Рассылка сообщений")]
        ]
    else:
        buttons = [
            [KeyboardButton(text="Abunəlikləri idarə et")],
            [KeyboardButton(text="İstifadəçiləri göstər")],
            [KeyboardButton(text="Mesaj göndər")]
        ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
