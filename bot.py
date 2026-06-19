users = set()

import asyncio
from datetime import datetime, timedelta
from collections import defaultdict

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

    if weekday == 2:
        return {
            "time": "19:00",
            "location": "Tempo | Restaurant",
            "map": "https://maps.app.goo.gl/NC6GyBSV6Z59giJH8"
        }

    if weekday == 5:
        return {
            "time": "18:00",
            "location": "LAVA Restobar & More",
            "map": "https://maps.app.goo.gl/UxUNkkknesw588ur8"
        }

    return {
        "time": "19:00",
        "location": "TBA",
        "map": ""
    }


# ===== KEYBOARD =====
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


# ===== HANDLER =====
@dp.message(F.text)
async def handler(message: types.Message):
    user_id = message.from_user.id
    text = message.text

    users.add(user_id)

    # ===== DATE STEP =====
    if user_id in user_data and user_data[user_id].get("step") == "date":
        user_data[user_id]["date"] = text
        user_data[user_id]["step"] = "name"
        await message.answer("Теперь имя:", reply_markup=menu_btn())
        return

    # ===== NAME STEP =====
    if user_id in user_data and user_data[user_id].get("step") == "name":
        user_data[user_id]["name"] = text
        user = user_data[user_id]

        telegram_id = user_id
        name = user.get("name")

        msg = f"""
🔥 Новая заявка

Тип: {user.get('type')}
Дата: {user.get('date', '-')}

👤 <a href="tg://user?id={telegram_id}">{name}</a>
"""

        await bot.send_message(ADMIN_ID, msg, parse_mode="HTML")

        # ===== EVENT SAVE =====
        user_date = user.get("date")
        if user_date:
            events[user_date].append({
                "user_id": telegram_id,
                "name": name
            })

        # ===== RESPONSE =====
        event_text = "🔥 Ты в игре"

        if user_date:
            try:
                day_num = int(user_date.split("(")[-1].replace(")", ""))
                event_date = datetime(datetime.now().year, datetime.now().month, day_num)

                info = get_event_info(event_date)

                event_text = (
                    f"🔥 Ты в игре\n"
                    f"📅 {user_date}\n"
                    f"🕖 {info['time']}\n"
                    f"📍 {info['location']}"
                )

                if info["map"]:
                    event_text += f"\n🔗 {info['map']}"

            except:
                pass

        await message.answer(event_text, reply_markup=main_menu())

        user_data.pop(user_id, None)
        return

    # ===== MENU =====
    if text == "/start" or text == "🏠 Главное меню":
        user_data.pop(user_id, None)
        await message.answer("🕴️ Phuket Mafia Club", reply_markup=main_menu())
        return

    # ===== SOCIAL =====
    if text == "🍸 Social Mafia":
        user_data[user_id] = {"type": "Social", "step": "date"}
        await message.answer("Выбери дату:", reply_markup=main_menu())
        return

    # ===== SPORT =====
    if text == "🧠 Sport Mafia":
        user_data[user_id] = {"type": "Sport", "step": "date"}
        await message.answer("Выбери дату:", reply_markup=main_menu())
        return

    # ===== PRIVATE =====
    if text == "🎉 Private Mafia":
        user_data[user_id] = {"type": "Private", "step": "date"}
        await message.answer("Напиши дату:", reply_markup=menu_btn())
        return

    # ===== PASS =====
    if text == "💳 Mafia Pass":
        user_data[user_id] = {"type": "Pass", "step": "date"}
        await message.answer("Выбери тариф:", reply_markup=menu_btn())
        return


# ===== REMINDER LOOP =====
async def reminder_loop():
    while True:
        now = datetime.now()

        for date_key, users_list in list(events.items()):
            try:
                day_num = int(date_key.split("(")[-1].replace(")", ""))
                event_date = datetime(now.year, now.month, day_num)

                diff = (event_date - now).total_seconds()

                if 23 * 3600 < diff < 25 * 3600:
                    info = get_event_info(event_date)

                    msg = (
                        "⏰ Напоминание!\n\n"
                        f"🕖 {info['time']}\n"
                        f"📍 {info['location']}\n"
                        f"{info['map']}"
                    )

                    for u in users_list:
                        await bot.send_message(u["user_id"], msg)

            except:
                pass

        await asyncio.sleep(3600)


# ===== RUN =====
async def main():
    asyncio.create_task(reminder_loop())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
