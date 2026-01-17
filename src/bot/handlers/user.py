from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from src.bot.keyboards.admin_kb import get_admin_keyboard
from src.db.session import Local_Session
from src.db.crud.user_crud import get_user, create_user, update_user
from src.db.crud.advertisement_crud import get_ad_by_id
from src.db.models.searchfilter import SearchFilter
from src.bot.keyboards.user_kb import get_user_keyboard
from src.bot.fsm.filter_fsm import FilterStates
from sqlalchemy import select

user_router = Router()

MAKES = {
    "abarth": 280,
    "acura": 28,
    "alfa romeo": 30,
    "anyang kinland": 859,
    "aprilia": 156,
    "arctic cat": 249,
    "aston martin": 86,
    "atv": 268,
    "audi": 9,
    "avatr": 419,
    "baic": 218,
    "bajaj": 327,
    "baw": 226,
    "benda": 642,
    "bentley": 19,
    "bestune": 387,
    "bmc": 136,
    "bmw": 3,
    "brilliance": 92,
    "brp": 736,
    "buick": 84,
    "bull motors": 378,
    "byd": 51,
    "c.moto": 395,
    "cadillac": 38,
    "can-am": 220,
    "cfmoto": 259,
    "changan": 163,
    "chery": 52,
    "chevrolet": 41,
    "chrysler": 10,
    "citroen": 27,
    "dacia": 76,
    "daewoo": 11,
    "daf": 91,
    "dayun": 148,
    "denza": 471,
    "dfsk": 405,
    "dnepr": 162,
    "dodge": 60,
    "dongfeng": 117,
    "ducati": 147,
    "faw": 79,
    "ferrari": 42,
    "fiat": 37,
    "ford": 2,
    "forthing": 478,
    "foton": 49,
    "freedom": 689,
    "fy": 870,
    "gac": 175,
    "gaz": 21,
    "geely": 72,
    "genesis": 376,
    "gmc": 82,
    "golden dragon": 773,
    "grandmoto": 466,
    "gst": 847,
    "gwm (great wall motor)": 50,
    "hao jiang": 142,
    "hao sui": 860,
    "haojue": 142,
    "harley-davidson": 140,
    "haval": 242,
    "hd k": 774,
    "honda": 12,
    "hongqi": 388,
    "howo": 110,
    "hummer": 13,
    "huzhou": 240,
    "hyosung": 167,
    "hyundai": 1,
    "i hon zda": 772,
    "ij": 64,
    "im": 424,
    "indian motorcycle": 411,
    "infiniti": 15,
    "iran khodro": 116,
    "isuzu": 74,
    "iveco": 67,
    "jac": 124,
    "jaguar": 35,
    "jeep": 36,
    "jetour": 384,
    "jiangmen": 462,
    "jianshe": 337,
    "jidu": 691,
    "jim": 864,
    "jmc": 109,
    "kaiyi": 390,
    "kamaz": 90,
    "karry": 420,
    "kawasaki": 139,
    "kayak": 374,
    "keeway": 338,
    "kg mobility": 473,
    "khazar": 282,
    "kia": 8,
    "ktm": 141,
    "kuba": 332,
    "lada (vaz)": 5,
    "lamborghini": 43,
    "land rover": 20,
    "leapmotor": 459,
    "lexus": 14,
    "li auto": 412,
    "lifan": 87,
    "lincoln": 46,
    "luaz": 103,
    "lynk & co": 414,
    "m-hero": 677,
    "mack": 329,
    "maextro": 867,
    "man": 112,
    "maple": 423,
    "marshal": 856,
    "maserati": 44,
    "maz": 100,
    "mazda": 26,
    "mercedes": 4,
    "mercedes-maybach": 252,
    "mg": 127,
    "mikilon": 769,
    "mini": 31,
    "minsk": 146,
    "mitsubishi": 6,
    "mondial": 286,
    "moskvich": 81,
    "moto guzzi": 416,
    "muravey": 243,
    "mv agusta": 158,
    "nama": 324,
    "neman": 283,
    "neta": 409,
    "nio": 415,
    "nissan": 7,
    "niu": 379,
    "omoda jaecoo": 866,
    "opel": 29,
    "otokar": 181,
    "paz": 114,
    "peugeot": 16,
    "polaris": 247,
    "polestar": 396,
    "pontiac": 48,
    "porsche": 32,
    "qj motor": 681,
    "raf": 105,
    "ravon": 272,
    "renault": 17,
    "renault samsung": 595,
    "rks": 333,
    "roewe": 171,
    "rolls-royce": 18,
    "rover": 78,
    "rox (polar stone)": 477,
    "royal enfield": 422,
    "saab": 80,
    "saipa": 94,
    "samauto": 377,
    "scania": 108,
    "scion": 251,
    "seat": 59,
    "seres aito": 460,
    "setra": 115,
    "shacman": 133,
    "shaolin": 132,
    "sharmax": 690,
    "shelby": 869,
    "shineray": 144,
    "skoda": 22,
    "skywell": 399,
    "smart": 61,
    "soueast": 402,
    "ssangyong": 45,
    "subaru": 34,
    "suzuki": 33,
    "sym": 380,
    "tatra": 98,
    "temsa": 128,
    "tesla": 245,
    "tofas": 39,
    "toyota": 23,
    "triumph": 233,
    "tufan": 385,
    "tvs": 464,
    "uaz": 53,
    "ural": 145,
    "vespa": 223,
    "vgv": 410,
    "victoria": 868,
    "voge": 857,
    "volkswagen": 24,
    "volta": 386,
    "volvo": 25,
    "voskhod": 150,
    "voyah": 417,
    "wuling": 404,
    "xiaomi": 680,
    "xpeng": 421,
    "yamaha": 138,
    "zaz": 57,
    "zaza": 851,
    "zeekr": 403,
    "zil": 85,
    "zonsen": 285,
    "zontes": 143,
    "zuk": 398,
    "zx auto": 217,
}

MODELS = {
    3: {
        "m5": 57,
        "x5": 40,
        "335": 35,
    },
    4: {
        "c200": 123,
    },
}

def get_make_id(make_name: str) -> int:
    return MAKES.get(make_name.lower())

def get_model_id(make_id: int, model_name: str) -> int:
    return MODELS.get(make_id, {}).get(model_name.lower())

texts = {
    "ru": {
        "start": "Привет! Выберите действие:",
        "lang_set": "Язык установлен на русский.",
        "choose_lang": "Выберите язык: /ru или /az",
        "filter_start": "Введите марку авто:",
        "model": "Введите модель:",
        "min_price": "Введите минимальную цену (AZN):",
        "max_price": "Введите максимальную цену (AZN):",
        "filter_saved": "Фильтр сохранен!",
        "subscription_required": "У вас нет активной подписки.",
        "my_filters": "Ваши фильтры:",
        "no_filters": "У вас нет активных фильтров.",
        "delete_filter": "Удалить"
    },
    "az": {
        "start": "Salam! Əməliyyatı seçin:",
        "lang_set": "Dil Azərbaycan dilinə quruldu.",
        "choose_lang": "Dili seçin: /ru və ya /az",
        "filter_start": "Avtomobil markasını daxil edin:",
        "model": "Modeli daxil edin:",
        "min_price": "Minimum qiyməti daxil edin (AZN):",
        "max_price": "Maksimum qiyməti daxil edin (AZN):",
        "filter_saved": "Filter saxlanıldı!",
        "subscription_required": "Aktiv abunəliyiniz yoxdur.",
        "my_filters": "Sizin filtrləriniz:",
        "no_filters": "Aktiv filtrləriniz yoxdur.",
        "delete_filter": "Sil"
    }
}

@user_router.message(Command("start"))
async def cmd_start(message: Message, language: str):
    user_id = message.from_user.id
    async with Local_Session() as session:
        user = await get_user(session, user_id)
        if not user:
            role = "admin" if user_id == 5343382918 else "user"
            subscription = True if role == "admin" else False
            user = await create_user(session, {"id": user_id, "username": message.from_user.username, "full_name": message.from_user.full_name, "role": role, "subscription": subscription})
    keyboard = get_user_keyboard(user.language) if user.role == "user" else get_admin_keyboard(user.language)
    await message.reply(texts[user.language]["start"], reply_markup=keyboard)

@user_router.message(F.text == "Язык / Dil")
async def toggle_lang(message: Message, user):
    new_lang = "az" if user.language == "ru" else "ru"
    user_id = message.from_user.id
    async with Local_Session() as session:
        await update_user(session, user_id, language=new_lang)
    keyboard = get_user_keyboard(new_lang) if user.role == "user" else get_admin_keyboard(new_lang)
    set_text = texts[new_lang]["lang_set"]
    await message.reply(set_text, reply_markup=keyboard)

@user_router.message(F.text.in_(["Настройка фильтров", "Filterləri tənzimlə"]))
async def start_filter(message: Message, state: FSMContext, user):
    if not user.subscription:
        await message.reply(texts[user.language]["subscription_required"])
        return
    await state.set_state(FilterStates.waiting_for_make)
    await message.reply(texts[user.language]["filter_start"])

@user_router.message(F.text.in_(["Просмотреть мои фильтры", "Filtrlərimi göstər"]))
async def view_filters(message: Message, user):
    if not user.subscription:
        await message.reply(texts[user.language]["subscription_required"])
        return
    async with Local_Session() as session:
        result = await session.execute(select(SearchFilter).where(SearchFilter.user_id == user.id))
        filters = result.scalars().all()
    
    if not filters:
        await message.reply(texts[user.language]["no_filters"])
        return
    
    keyboard = []
    for f in filters:
        keyboard.append([InlineKeyboardButton(text=f.label, callback_data=f"filter_view_{f.id}")])
        keyboard.append([InlineKeyboardButton(text=texts[user.language]["delete_filter"], callback_data=f"filter_delete_{f.id}")])
    
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.reply(texts[user.language]["my_filters"], reply_markup=markup)

async def update_filters_message(message: Message, user):
    if not user.subscription:
        await message.edit_text(texts[user.language]["subscription_required"])
        return
    async with Local_Session() as session:
        result = await session.execute(select(SearchFilter).where(SearchFilter.user_id == user.id))
        filters = result.scalars().all()
    
    if not filters:
        await message.edit_text(texts[user.language]["no_filters"])
        return
    
    keyboard = []
    for f in filters:
        keyboard.append([InlineKeyboardButton(text=f.label, callback_data=f"filter_view_{f.id}")])
        keyboard.append([InlineKeyboardButton(text=texts[user.language]["delete_filter"], callback_data=f"filter_delete_{f.id}")])
    
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.edit_text(texts[user.language]["my_filters"], reply_markup=markup)

@user_router.callback_query(F.data.startswith("filter_view_"))
async def view_filter_callback(callback: CallbackQuery):
    await callback.answer()  # Просто закрыть

@user_router.callback_query(F.data.startswith("filter_delete_"))
async def delete_filter_callback(callback: CallbackQuery, user):
    filter_id = int(callback.data.split("_")[2])
    async with Local_Session() as session:
        filter_obj = await session.get(SearchFilter, filter_id)
        if filter_obj and filter_obj.user_id == user.id:
            await session.delete(filter_obj)
            await session.commit()
            await callback.answer("Фильтр удален" if user.language == "ru" else "Filter silindi")
            await update_filters_message(callback.message, user)
        else:
            await callback.answer("Ошибка" if user.language == "ru" else "Xəta")

@user_router.message(FilterStates.waiting_for_make)
async def process_make(message: Message, state: FSMContext, user):
    await state.update_data(make=message.text)
    await state.set_state(FilterStates.waiting_for_model)
    await message.reply(texts[user.language]["model"])

@user_router.message(FilterStates.waiting_for_model)
async def process_model(message: Message, state: FSMContext, user):
    await state.update_data(model=message.text)
    await state.set_state(FilterStates.waiting_for_min_price)
    await message.reply(texts[user.language]["min_price"])

@user_router.message(FilterStates.waiting_for_min_price)
async def process_min_price(message: Message, state: FSMContext, user):
    try:
        price = int(message.text)
        if price < 0:
            raise ValueError
        await state.update_data(min_price=str(price))
        await state.set_state(FilterStates.waiting_for_max_price)
        await message.reply(texts[user.language]["max_price"])
    except ValueError:
        await message.reply("Введите корректную цену (целое положительное число)")

@user_router.message(FilterStates.waiting_for_max_price)
async def process_max_price(message: Message, state: FSMContext, user):
    try:
        price = int(message.text)
        if price < 0:
            raise ValueError
        await state.update_data(max_price=str(price))
        data = await state.get_data()
        user_id = message.from_user.id
        make_name = data['make']
        model_name = data['model']
        make_id = get_make_id(make_name)
        model_id = get_model_id(make_id, model_name) if make_id else None
        min_p = data['min_price']
        max_p = data['max_price']
        url = f"https://turbo.az/autos?q[currency]=azn&q[price_from]={min_p}&q[price_to]={max_p}"
        if make_id:
            url += f"&q[make][]={make_id}"
        if model_id:
            url += f"&q[model][]={model_id}"
        label = f"{data['make']} {data['model']} {min_p}-{max_p}"

        async with Local_Session() as session:
            filter_obj = SearchFilter(user_id=user_id, query_url=url, label=label)
            session.add(filter_obj)
            await session.commit()
            from src.db.session import Local_Session as LS
            async with LS() as sess:
                await update_user(sess, user_id, subscription=True)

        await state.clear()
        keyboard = get_user_keyboard(user.language)

        if user.language == "ru":
            filter_msg = f"Теперь вам будут приходить предложения по фильтру: {label} AZN"
        else:
            filter_msg = f"İndi sizə filtr üzrə təkliflər gələcək: {label} AZN"

        await message.reply(texts[user.language]["filter_saved"] + "\n\n" + filter_msg, reply_markup=keyboard)
    except ValueError:
        await message.reply("Введите корректную цену (целое положительное число)")

