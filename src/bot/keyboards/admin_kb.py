from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_admin_keyboard(language: str) -> ReplyKeyboardMarkup:
    if language == "ru":
        buttons = [
            [KeyboardButton(text="Управление подписками"), KeyboardButton(text="Список команд")],
            [KeyboardButton(text="Просмотр пользователей")],
            [KeyboardButton(text="Рассылка сообщений")],
            [KeyboardButton(text="Настройка фильтров"), KeyboardButton(text="Просмотреть мои фильтры")]
        ]
    else:
        buttons = [
            [KeyboardButton(text="Abunəlikləri idarə et"), KeyboardButton(text="Əmrlər siyahısı")],
            [KeyboardButton(text="İstifadəçiləri göstər")],
            [KeyboardButton(text="Mesaj göndər")],
            [KeyboardButton(text="Filterləri tənzimlə"), KeyboardButton(text="Filtrlərimi göstər")]
        ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
