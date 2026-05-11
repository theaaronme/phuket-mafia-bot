import asyncio
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = "8663305968:AAHBgI7L40v-CKFpLY7iOMqSZjQPb4UongE"
ADMIN_ID = 5797862303

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_data = {}

# ===== ДНИ НА РУССКОМ =====
days_ru = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

def format_date(day):
    return f"{days_ru[day.weekday()]} ({day.strftime('%d.%m')})"

# ===== КНОПКИ =====

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🍸 Social Mafia"), KeyboardButton(text="🧠 Sport Mafia")],
            [KeyboardButton(text="🎉 Private Mafia"), KeyboardButton(text="💳 Mafia Pass")],
            [KeyboardButton(text="🤝 Сотрудничество"), KeyboardButton(text="📕 Правила")]
        ],
        resize_keyboard=True
    )

def menu_btn():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🏠 Главное меню")]],
        resize_keyboard=True
    )

# ===== ДАТЫ =====

def get_next_days(target_weekdays, count):
    today = datetime.now()
    result = []

    for i in range(14):
        day = today + timedelta(days=i)
        if day.weekday() in target_weekdays:
            result.append(day)
        if len(result) == count:
            break

    return result

def show_dates(user_type):
    if user_type == "Social":
        days = get_next_days([2, 5], 2)
    else:
        days = get_next_days([3], 1)

    # 👉 если 2 даты — в один ряд
    if len(days) == 2:
        keyboard = [[
            KeyboardButton(text=format_date(days[0])),
            KeyboardButton(text=format_date(days[1]))
        ]]
    else:
        keyboard = [[KeyboardButton(text=format_date(days[0]))]]

    keyboard.append([KeyboardButton(text="🏠 Главное меню")])

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# ===== ОБРАБОТКА =====

@dp.message()
async def handler(message: types.Message):
    user_id = message.from_user.id
    text = message.text

    # ===== ГЛАВНОЕ МЕНЮ =====
    if text == "/start" or text == "🏠 Главное меню":
        user_data.pop(user_id, None)

        await message.answer(
            "🕴️ Phuket Mafia Club\n\n"
            "🍸 Social — городская мафия + знакомства + нетворкинг\n"
            "🧠 Sport — спортивная мафия, всего 10 игроков\n"
            "🎉 Private — мафия под ключ для вашей компании\n"
            "💳 Pass — месячная подписка\n",
            reply_markup=main_menu()
        )

    # ===== SOCIAL =====
    elif text == "🍸 Social Mafia":
        user_data[user_id] = {"type": "Social", "step": "date"}

        await message.answer(
            "🍸 Social Mafia\n\n"
            "— лёгкая игра\n"
            "— знакомства\n"
            "— нетворкинг\n\n"
            "💰 500฿\n🕖 19:00\n\n"
            "Выбери дату:",
            reply_markup=show_dates("Social")
        )

    # ===== SPORT =====
    elif text == "🧠 Sport Mafia":
        user_data[user_id] = {"type": "Sport", "step": "date"}

        await message.answer(
            "🧠 Sport Mafia\n\n"
            "— 10 игроков\n"
            "— логика и давление\n\n"
            "💰 1000฿\n🕖 19:00\n\n"
            "Выбери дату:",
            reply_markup=show_dates("Sport")
        )

    # ===== PRIVATE =====
    elif text == "🎉 Private Mafia":
        user_data[user_id] = {"type": "Private", "step": "date"}

        await message.answer(
            "🎉 Private Mafia\n\n"
            "— день рождения\n"
            "— корпоратив\n"
            "— вилла\n\n"
            "Напиши дату и формат (пример: 5 мая, день рождения):",
            reply_markup=menu_btn()
        )

    # ===== PASS =====
    elif text == "💳 Mafia Pass":
        user_data[user_id] = {"type": "Pass", "step": "plan"}

        keyboard = [
            [
                KeyboardButton(text="Light (Social)"),
                KeyboardButton(text="Pro (Sport)"),
                KeyboardButton(text="Unlimited")
            ],
            [KeyboardButton(text="🏠 Главное меню")]
        ]

        await message.answer(
            "💳 Подписка:\n— выгоднее\n— приоритет\n\nВыбери тариф:",
            reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
        )
    # ===== PASS ВЫБОР =====
    elif user_id in user_data and user_data[user_id].get("step") == "plan":
        user_data[user_id]["plan"] = text
        user_data[user_id]["step"] = "name"
        await message.answer("Напиши своё имя:", reply_markup=menu_btn())

    # ===== СОТРУДНИЧЕСТВО =====
    elif text == "🤝 Сотрудничество":
        user_data[user_id] = {"type": "Collab", "step": "name"}
        await message.answer("Напиши своё имя:", reply_markup=menu_btn())

    # ===== ПРАВИЛА =====
    elif text == "📕 Правила":
        await message.answer(
            "📕 Правила:\n— уважение\n— без вскрытий\n",
            reply_markup=menu_btn()
        )

    # ===== ДАТА =====
    elif user_id in user_data and user_data[user_id].get("step") == "date":
        user_data[user_id]["date"] = text
        user_data[user_id]["step"] = "name"
        await message.answer("Напиши своё имя:", reply_markup=menu_btn())

    # ===== ИМЯ =====
    elif user_id in user_data and user_data[user_id].get("step") == "name":
        user_data[user_id]["name"] = text
        user_data[user_id]["step"] = "username"
        await message.answer("📲 Напиши свой Telegram ник:", reply_markup=menu_btn())

    # ===== НИК =====
    # ===== НИК =====
    elif user_id in user_data and user_data[user_id].get("step") == "username":
        username = text.strip()

        # убираем @ если есть
        if username.startswith("@"):
            username = username[1:]

        # проверка: только английские буквы, цифры и _
        if not username.isascii() or not username.replace("_", "").isalnum():
            await message.answer(
                "❗️Укажи корректный Telegram ник\n\n"
                "— только английские буквы\n"
                "— можно цифры и _\n\n"
                "Пример: theaaronme",
                reply_markup=menu_btn()
            )
            return

        username = "@" + username
        user_data[user_id]["username"] = username

        user = user_data[user_id]

        msg = f"""
🔥 Новая заявка

Тип: {user.get('type')}
Дата: {user.get('date', '-')}
Тариф: {user.get('plan', '-')}

Имя: {user.get('name')}
Ник: {user.get('username')}
"""

        await bot.send_message(ADMIN_ID, msg)

        if user["type"] in ["Social", "Sport"]:
            await message.answer(
                "🔥 Ты в игре\n\n📍 Локация позже\n🕖 19:00\n\n❗️Не опаздывай",
                reply_markup=main_menu()
            )
        else:
            await message.answer(
                "🔥 Заявка отправлена\n\nМы свяжемся с тобой",
                reply_markup=main_menu()
            )

        user_data.pop(user_id)
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
