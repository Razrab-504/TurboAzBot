from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_user_keyboard(language: str) -> ReplyKeyboardMarkup:
    if language == "ru":
        buttons = [
            [KeyboardButton(text="Язык / Dil")],
            [KeyboardButton(text="Настройка фильтров"), KeyboardButton(text="Просмотреть мои фильтры")]
        ]
    else:
        buttons = [
            [KeyboardButton(text="Язык / Dil")],
            [KeyboardButton(text="Filterləri tənzimlə"), KeyboardButton(text="Filtrlərimi göstər")]
        ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
