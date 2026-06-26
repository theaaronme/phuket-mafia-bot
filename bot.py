users = set()

import asyncio
from datetime import datetime, timedelta
from collections import defaultdict
import re

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = "8663305968:AAGr0u_u-IA0Akp-dBK8YF221bmu0oBJKHM"
ADMIN_ID = 5797862303

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_data = {}
events = defaultdict(list)


# ===== ДНИ =====
days_ru = [
    "Понедельник", "Вторник", "Среда",
    "Четверг", "Пятница", "Суббота", "Воскресенье"
]


def format_date(day):
    return f"{days_ru[day.weekday()]} ({day.strftime('%d.%m')})"


# ===== ЛОКАЦИИ =====
def get_event_info(date_obj):
    weekday = date_obj.weekday()

    if weekday == 2:  # Wednesday
        return {
            "time": "19:00",
            "location": "Tempo | Restaurant",
            "map": "https://maps.app.goo.gl/NC6GyBSV6Z59giJH8"
        }

    if weekday == 5:  # Saturday
        return {
            "time": "18:00",
            "location": "SHISHKA & UMAY",
            "map": "https://maps.app.goo.gl/K2yuMXsqQvwb9agf8?g_st=ic"
        }

    return {
        "time": "19:00",
        "location": "TBA",
        "map": ""
    }


# ===== КЛИКАБЕЛЬНАЯ ЛОКАЦИЯ =====
def format_location(info):
    if not info:
        return "TBA"

    if not info.get("map"):
        return info.get("location", "TBA")

    return f'<a href="{info["map"]}">{info["location"]}</a>'


# ===== PARSE DATE =====
def parse_date(text: str):
    match = re.search(r"\((\d{2})\.(\d{2})\)", text)
    if not match:
        return None

    day = int(match.group(1))
    month = int(match.group(2))

    return datetime(datetime.now().year, month, day)


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

    keyboard = []

    if len(days) == 2:
        keyboard.append([
            KeyboardButton(text=format_date(days[0])),
            KeyboardButton(text=format_date(days[1]))
        ])
    else:
        keyboard.append([KeyboardButton(text=format_date(days[0]))])

    keyboard.append([KeyboardButton(text="🏠 Главное меню")])

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


# ===== HANDLER =====
@dp.message(F.text)
async def handler(message: types.Message):
    user_id = message.from_user.id
    text = message.text

    users.add(user_id)

    # ===== MENU =====
    if text == "/start" or text == "🏠 Главное меню":
        user_data.pop(user_id, None)
        await message.answer("🕴️ Phuket Mafia Club", reply_markup=main_menu())

    # ===== SOCIAL =====
    elif text == "🍸 Social Mafia":
        user_data[user_id] = {"type": "Social", "step": "date"}
        await message.answer("Выбери дату:", reply_markup=show_dates("Social"))

    # ===== SPORT =====
    elif text == "🧠 Sport Mafia":
        user_data[user_id] = {"type": "Sport", "step": "date"}
        await message.answer("Выбери дату:", reply_markup=show_dates("Sport"))

    # ===== DATE =====
    elif user_id in user_data and user_data[user_id].get("step") == "date":
        user_data[user_id]["date"] = text
        user_data[user_id]["step"] = "name"
        await message.answer("Теперь имя:", reply_markup=menu_btn())

    # ===== NAME =====
    elif user_id in user_data and user_data[user_id].get("step") == "name":
        user_data[user_id]["name"] = text
        user = user_data[user_id]

        telegram_id = user_id
        name = user.get("name")

        event_date = parse_date(user.get("date", ""))
        info = get_event_info(event_date) if event_date else None

        # ===== ADMIN MSG =====
        msg_admin = f"""
🔥 НОВАЯ ЗАПИСЬ

📌 Тип: {user.get('type')}
📅 Дата: {user.get('date', '-')}

🕖 Время: {info['time'] if info else '19:00'}
📍 Локация: {format_location(info)}

👤 <a href="tg://user?id={telegram_id}">{name}</a>

🧠 USER ID: {telegram_id}
"""

        await bot.send_message(
            ADMIN_ID,
            msg_admin,
            parse_mode="HTML"
        )

        # ===== USER MSG =====
        user_msg = f"""
🔥 Ты в игре

📅 {user.get('date', '-')}
🕖 {info['time'] if info else '19:00'}
📍 {format_location(info)}

👤 {name}
"""

        await message.answer(
    user_msg,
    reply_markup=main_menu(),
    parse_mode="HTML"
)

        # ===== SAVE EVENT =====
        if event_date:
            events[event_date.strftime("%d.%m")].append({
                "user_id": telegram_id,
                "name": name
            })

        user_data.pop(user_id, None)


# ===== RUN =====
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
