import asyncio
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = "8663305968:AAGr0u_u-IA0Akp-dBK8YF221bmu0oBJKHM"
ADMIN_ID = 5797862303

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_data = {}

# ===== ДНИ =====
days_ru = [
    "Понедельник", "Вторник", "Среда",
    "Четверг", "Пятница", "Суббота", "Воскресенье"
]

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

    keyboard = []

    if len(days) == 2:
        keyboard.append([
            KeyboardButton(text=format_date(days[0])),
            KeyboardButton(text=format_date(days[1]))
        ])
    elif len(days) == 1:
        keyboard.append([KeyboardButton(text=format_date(days[0]))])

    keyboard.append([KeyboardButton(text="🏠 Главное меню")])

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


# ===== HANDLER =====
@dp.message(F.text)
async def handler(message: types.Message):
    user_id = message.from_user.id
    text = message.text

    # ===== START / MENU =====
    if text == "/start" or text == "🏠 Главное меню":
        user_data.pop(user_id, None)

        await message.answer(
            "🕴️ Phuket Mafia Club\n\n"
            "🍸 Social — городская мафия + знакомства\n"
            "🧠 Sport — 10 игроков, хардкор логика\n"
            "🎉 Private — под вашу компанию\n"
            "💳 Pass — подписка\n",
            reply_markup=main_menu()
        )

    # ===== SOCIAL =====
    elif text == "🍸 Social Mafia":
        user_data[user_id] = {"type": "Social", "step": "date"}

        await message.answer(
            "🍸 Social Mafia\n\nВыбери дату:",
            reply_markup=show_dates("Social")
        )

    # ===== SPORT =====
    elif text == "🧠 Sport Mafia":
        user_data[user_id] = {"type": "Sport", "step": "date"}

        await message.answer(
            "🧠 Sport Mafia\n\nВыбери дату:",
            reply_markup=show_dates("Sport")
        )

    # ===== PRIVATE =====
    elif text == "🎉 Private Mafia":
        user_data[user_id] = {"type": "Private", "step": "date"}

        await message.answer(
            "🎉 Напиши дату и формат:\nпример: 5 мая, день рождения",
            reply_markup=menu_btn()
        )

    # ===== PASS =====
    elif text == "💳 Mafia Pass":
        user_data[user_id] = {"type": "Pass", "step": "plan"}

        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Light (Social)"),
                    KeyboardButton(text="Pro (Sport)"),
                    KeyboardButton(text="Unlimited")
                ],
                [KeyboardButton(text="🏠 Главное меню")]
            ],
            resize_keyboard=True
        )

        await message.answer(
            "💳 Выбери тариф:",
            reply_markup=keyboard
        )

    # ===== PASS PLAN =====
    elif user_id in user_data and user_data[user_id].get("step") == "plan":
        user_data[user_id]["plan"] = text
        user_data[user_id]["step"] = "name"

        await message.answer("Напиши своё имя:", reply_markup=menu_btn())

    # ===== COOP =====
    elif text == "🤝 Сотрудничество":
        user_data[user_id] = {"type": "Collab", "step": "name"}

        await message.answer("Напиши своё имя:", reply_markup=menu_btn())

    # ===== RULES =====
    elif text == "📕 Правила":
        await message.answer(
            "📕 Правила:\n— уважение\n— без токсичности",
            reply_markup=menu_btn()
        )

    # ===== DATE =====
    elif user_id in user_data and user_data[user_id].get("step") == "date":
        user_data[user_id]["date"] = text
        user_data[user_id]["step"] = "name"

        await message.answer("Напиши своё имя:", reply_markup=menu_btn())

    # ===== NAME (FIXED PLACE) =====
    elif user_id in user_data and user_data[user_id].get("step") == "name":
        user_data[user_id]["name"] = text
        user = user_data[user_id]

        msg = (
            f"🔥 Новая заявка\n\n"
            f"Тип: {user.get('type')}\n"
            f"Дата: {user.get('date', '-')}\n"
            f"Тариф: {user.get('plan', '-')}\n\n"
            f"👤 {user.get('name')}"
        )

        await bot.send_message(ADMIN_ID, msg)

        if user["type"] in ["Social", "Sport"]:
            await message.answer(
                "🔥 Ты в игре\n📍 Локация позже\n🕖 19:00",
                reply_markup=main_menu()
            )
        else:
            await message.answer(
                "🔥 Заявка отправлена\nМы свяжемся с тобой",
                reply_markup=main_menu()
            )

        user_data.pop(user_id, None)


# ===== RUN =====
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
