# Turbo.az Auto Search Bot

Telegram бот для автоматического поиска и рассылки объявлений о продаже автомобилей с сайта [Turbo.az](https://turbo.az).

## Особенности

- **Парсинг объявлений**: Автоматический сбор свежих объявлений с Turbo.az по заданным фильтрам.
- **Персональные фильтры**: Пользователи могут создавать фильтры по марке, модели, цене и другим параметрам.
- **Автоматическая рассылка**: Каждые 30 секунд бот проверяет новые объявления и отправляет их подписанным пользователям.
- **Многоязычность**: Поддержка русского и азербайджанского языков.
- **Админ панель**: Управление подписками пользователей, просмотр списка пользователей.
- **Без повторов**: Каждое объявление отправляется пользователю только один раз.
- **Гибкая фильтрация**: Точная фильтрация по модели автомобиля.

## Технологии

- **Python 3.11+**
- **Aiogram** - фреймворк для Telegram ботов
- **SQLAlchemy** - ORM для работы с базой данных
- **PostgreSQL** - база данных
- **BeautifulSoup** - парсинг HTML
- **AioHTTP** - асинхронные HTTP запросы

## Установка и запуск

### Предварительные требования

- Python 3.11+
- PostgreSQL база данных
- Токен Telegram бота (получить у [@BotFather](https://t.me/botfather))

### Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/your-repo/turbo-az-bot.git
   cd turbo-az-bot
   ```

2. Создайте виртуальное окружение:
   ```bash
   python -m venv venv
   source venv/bin/activate  # На Windows: venv\Scripts\activate
   ```

3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

4. Настройте базу данных:
   - Создайте базу данных PostgreSQL
   - Запустите скрипт создания таблиц:
     ```bash
     python create_database.py
     ```

5. Настройте переменные окружения в файле `.env`:
   ```
   BOT_TOKEN=your_telegram_bot_token
   ADMIN_ID=your_telegram_user_id
   DB_NAME=your_db_name
   DB_USER=your_db_user
   DB_PASS=your_db_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

### Запуск

```bash
python main.py
```

## Использование

### Для пользователей

1. **Старт**: Напишите `/start` боту.
2. **Язык**: Выберите язык с помощью кнопки "Язык / Dil".
3. **Создание фильтра**:
   - Выберите "Настройка фильтров" / "Filterləri tənzimlə"
   - Введите марку автомобиля
   - Введите модель
   - Введите минимальную цену
   - Введите максимальную цену
4. **Просмотр фильтров**: Используйте "Просмотреть мои фильтры" для управления активными фильтрами.
5. **Получение уведомлений**: Бот автоматически отправляет новые объявления по вашим фильтрам каждые 30 секунд.

### Для админов

- **Выдача подписки**: Используйте команду `/grant_sub <user_id>` для активации подписки пользователя.
- **Отзыв подписки**: Используйте `/revoke_sub <user_id>` для отключения подписки (автоматически удаляет все фильтры пользователя).
- **Просмотр пользователей**: Через админ панель можно посмотреть список всех пользователей.

## Структура проекта

```
src/
├── bot/
│   ├── handlers/
│   │   ├── admin.py          # Обработчики админ команд
│   │   └── user.py           # Обработчики пользовательских команд
│   ├── keyboards/
│   │   ├── admin_kb.py       # Клавиатуры для админов
│   │   └── user_kb.py        # Клавиатуры для пользователей
│   ├── middlewares/
│   │   └── language_middleware.py  # Middleware для языка
│   ├── filters/
│   │   └── admin_filter.py   # Фильтр для проверки админов
│   └── fsm/
│       └── filter_fsm.py     # Машина состояний для создания фильтров
├── db/
│   ├── models/               # Модели базы данных
│   ├── crud/                 # CRUD операции
│   ├── config.py             # Конфигурация БД
│   ├── session.py            # Сессии SQLAlchemy
│   └── base.py               # Базовый класс для моделей
└── scraper/
    ├── parser.py             # Основной парсер и рассылка
    └── turbo_parser.py       # Парсер объявлений с Turbo.az
```

## База данных

Проект использует PostgreSQL с асинхронным драйвером asyncpg.

### Модели

- **User**: Пользователи бота (ID, подписка, язык и т.д.)
- **SearchFilter**: Фильтры поиска пользователей
- **Advertisement**: Кэш объявлений
- **SentAd**: Отслеживание отправленных объявлений

## Безопасность

- Проверка прав админа по ID
- Валидация ввода пользователей
- Защита от SQL-инъекций через SQLAlchemy
- Ограничение частоты запросов к сайту

## Лицензия

Этот проект предназначен только для образовательных целей. Использование для коммерческих целей требует соблюдения условий сайта Turbo.az.

## Контакты

Для вопросов и предложений создавайте issues в репозитории.

---

# Turbo.az Auto Search Bot

Telegram bot for automatic search and mailing of car sales ads from [Turbo.az](https://turbo.az).

## Features

- **Ad parsing**: Automatic collection of fresh ads from Turbo.az by specified filters.
- **Personal filters**: Users can create filters by make, model, price and other parameters.
- **Automatic mailing**: Every 30 seconds the bot checks new ads and sends them to subscribed users.
- **Multilingual**: Support for Russian and Azerbaijani languages.
- **Admin panel**: User subscription management, user list viewing.
- **No duplicates**: Each ad is sent to user only once.
- **Flexible filtering**: Precise filtering by car model.

## Technologies

- **Python 3.11+**
- **Aiogram** - framework for Telegram bots
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - database
- **BeautifulSoup** - HTML parsing
- **AioHTTP** - asynchronous HTTP requests

## Installation and Launch

### Prerequisites

- Python 3.11+
- PostgreSQL database
- Telegram bot token (get from [@BotFather](https://t.me/botfather))

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/turbo-az-bot.git
   cd turbo-az-bot
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Setup database:
   - Create PostgreSQL database
   - Run table creation script:
     ```bash
     python create_database.py
     ```

5. Configure environment variables in `.env` file:
   ```
   BOT_TOKEN=your_telegram_bot_token
   ADMIN_ID=your_telegram_user_id
   DB_NAME=your_db_name
   DB_USER=your_db_user
   DB_PASS=your_db_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

### Launch

```bash
python main.py
```

## Usage

### For users

1. **Start**: Write `/start` to the bot.
2. **Language**: Select language using "Язык / Dil" button.
3. **Create filter**:
   - Select "Настройка фильтров" / "Filterləri tənzimlə"
   - Enter car make
   - Enter model
   - Enter minimum price
   - Enter maximum price
4. **View filters**: Use "Просмотреть мои фильтры" to manage active filters.
5. **Receive notifications**: Bot automatically sends new ads matching your filters every 30 seconds.

### For admins

- **Grant subscription**: Use `/grant_sub <user_id>` to activate user subscription.
- **Revoke subscription**: Use `/revoke_sub <user_id>` to deactivate subscription (automatically deletes all user filters).
- **View users**: Admin panel allows viewing all users list.

## Project Structure

```
src/
├── bot/
│   ├── handlers/
│   │   ├── admin.py          # Admin command handlers
│   │   └── user.py           # User command handlers
│   ├── keyboards/
│   │   ├── admin_kb.py       # Admin keyboards
│   │   └── user_kb.py        # User keyboards
│   ├── middlewares/
│   │   └── language_middleware.py  # Language middleware
│   ├── filters/
│   │   └── admin_filter.py   # Admin check filter
│   └── fsm/
│       └── filter_fsm.py     # Filter creation state machine
├── db/
│   ├── models/               # Database models
│   ├── crud/                 # CRUD operations
│   ├── config.py             # DB configuration
│   ├── session.py            # SQLAlchemy sessions
│   └── base.py               # Base model class
└── scraper/
    ├── parser.py             # Main parser and mailing
    └── turbo_parser.py       # Turbo.az ad parser
```

## Database

The project uses PostgreSQL with asyncpg async driver.

### Models

- **User**: Bot users (ID, subscription, language etc.)
- **SearchFilter**: User search filters
- **Advertisement**: Ad cache
- **SentAd**: Tracking sent ads

## Security

- Admin rights check by ID
- User input validation
- SQL injection protection via SQLAlchemy
- Site request rate limiting

## License

This project is for educational purposes only. Commercial use requires compliance with Turbo.az terms.

## Contacts

For questions and suggestions create issues in the repository.