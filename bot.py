users = set()

import asyncio
from collections import defaultdict
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = "8663305968:AAGr0u_u-IA0Akp-dBK8YF221bmu0oBJKHM"
ADMIN_ID = 5797862303

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_data = {}

# ===== СОБЫТИЯ =====
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
            "location": "LAVA Restobar & More",
            "map": "https://maps.app.goo.gl/UxUNkkknesw588ur8"
        }

    return {
        "time": "19:00",
        "location": "TBA",
        "map": ""
    }


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

    # ===== BROADCAST =====
    if user_id == ADMIN_ID and text.startswith("/broadcast"):
        msg_to_send = text.replace("/broadcast", "").strip()

        if msg_to_send:
            sent, failed = 0, 0

            for uid in list(users):
                try:
                    await bot.send_message(uid, msg_to_send)
                    sent += 1
                    await asyncio.sleep(0.03)
                except:
                    failed += 1

            await message.answer(f"📢 Sent: {sent} | Failed: {failed}")
        return

    # ===== MENU =====
    if text in ["/start", "🏠 Главное меню"]:
        user_data.pop(user_id, None)
        await message.answer("🕴️ Phuket Mafia Club", reply_markup=main_menu())
        return

    # ===== SOCIAL =====
    if text == "🍸 Social Mafia":
        user_data[user_id] = {"type": "Social", "step": "date"}
        await message.answer("Выбери дату:", reply_markup=show_dates("Social"))
        return

    # ===== SPORT =====
    if text == "🧠 Sport Mafia":
        user_data[user_id] = {"type": "Sport", "step": "date"}
        await message.answer("Выбери дату:", reply_markup=show_dates("Sport"))
        return

    # ===== PRIVATE =====
    if text == "🎉 Private Mafia":
        user_data[user_id] = {"type": "Private", "step": "date"}
        await message.answer("Напиши дату:", reply_markup=menu_btn())
        return

    # ===== PASS =====
    if text == "💳 Mafia Pass":
        user_data[user_id] = {"type": "Pass", "step": "plan"}
        await message.answer("Выбери тариф:", reply_markup=menu_btn())
        return

    # ===== PLAN =====
    if user_id in user_data and user_data[user_id].get("step") == "plan":
        user_data[user_id]["plan"] = text
        user_data[user_id]["step"] = "name"
        await message.answer("Напиши имя:", reply_markup=menu_btn())
        return

    # ===== COOP =====
    if text == "🤝 Сотрудничество":
        user_data[user_id] = {"type": "Collab", "step": "name"}
        await message.answer("Напиши имя:", reply_markup=menu_btn())
        return

    # ===== RULES =====
    if text == "📕 Правила":
        await message.answer("Правила: уважение", reply_markup=menu_btn())
        return

    # ===== DATE =====
    if user_id in user_data and user_data[user_id].get("step") == "date":
        user_data[user_id]["date"] = text
        user_data[user_id]["step"] = "name"
        await message.answer("Теперь имя:", reply_markup=menu_btn())
        return

    # ===== NAME + SAVE EVENT =====
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

        # ===== SAVE EVENT =====
        date_text = user.get("date")
        if date_text:
            events[date_text].append({
                "user_id": user_id,
                "name": name
            })

        await message.answer("🔥 Готово", reply_markup=main_menu())
        user_data.pop(user_id, None)
        return


# ===== REMINDER SYSTEM =====
async def reminder_loop():
    while True:
        now = datetime.now()

        for date_text, users_list in list(events.items()):
            try:
                day_num = int(date_text.split("(")[-1].replace(")", "").split(".")[0])
                month_num = int(date_text.split("(")[-1].replace(")", "").split(".")[1])

                event_date = datetime(now.year, month_num, day_num)

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
                        try:
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
