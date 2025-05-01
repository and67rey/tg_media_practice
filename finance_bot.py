import os
import random
import requests

import asyncio
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import sqlite3
import logging
from dotenv import load_dotenv

load_dotenv('.env')
API_TOKEN = os.getenv("API_TOKEN")
ER_API_KEY = os.getenv("Exchange_rate_API")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

button_registr = KeyboardButton(text="Регистрация в телеграм боте")
button_exchange_rates = KeyboardButton(text="Курс валют")
button_tips = KeyboardButton(text="Советы по экономии")
button_finances = KeyboardButton(text="Личные финансы")

keyboards = ReplyKeyboardMarkup(keyboard=[
    [button_registr, button_exchange_rates],
    [button_tips, button_finances]
    ], resize_keyboard=True)

conn = sqlite3.connect('user.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    telegram_id INTEGER UNIQUE,
    name TEXT,
    category1 TEXT,
    category2 TEXT,
    category3 TEXT,
    expenses1 REAL,
    expenses2 REAL,
    expenses3 REAL
    )
''')
conn.commit()
conn.close()

class FinancesForm(StatesGroup):
    category1 = State()
    expenses1 = State()
    category2 = State()
    expenses2 = State()
    category3 = State()
    expenses3 = State()


@dp.message(Command('start'))
async def send_start(message: Message):
    await message.answer("Привет! Я ваш личный финансовый помощник. Выберите одну из опций в меню:", reply_markup=keyboards)

@dp.message(F.text == "Регистрация в телеграм боте")
async def registration(message: Message):
    telegram_id = message.from_user.id
    name = message.from_user.full_name
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM users WHERE telegram_id = ?''', (telegram_id,))
    user = cursor.fetchone()
    if user:
        register_text = ("Вы уже зарегистрированы!\n"
                         f"Telegram ID: {telegram_id}\n"
                         f"Полное имя: {name}")
        conn.close()
        await message.answer(register_text)
    else:
        cursor.execute('''INSERT INTO users (telegram_id, name) VALUES (?, ?)''', (telegram_id, name))
        conn.commit()
        conn.close()
        register_text = ("Вы успешно зарегистрированы!\n"
                f"Telegram ID: {telegram_id}\n"
                f"Полное имя: {name}")
        await message.answer(register_text)

@dp.message(F.text == "Курс валют")
async def exchange_rates(message: Message):
    url = f"https://v6.exchangerate-api.com/v6/{ER_API_KEY}/latest/USD"
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code != 200:
            await message.answer("Не удалось получить данные о курсе валют!")
            return
        usd_to_rub = data['conversion_rates']['RUB']
        usd_to_eur = data['conversion_rates']['EUR']
        eur_to_usd = 1 / usd_to_eur
        euro_to_rub = eur_to_usd * usd_to_rub
        await message.answer(f"1 USD - {usd_to_rub:.2f}  RUB\n"
                             f"1 EUR - {euro_to_rub:.2f}  RUB")
    except:
        await message.answer("Произошла ошибка")

@dp.message(F.text == "Советы по экономии")
async def send_tips(message: Message):
    tips = [
        "Совет 1: Ведите бюджет и следите за своими расходами.",
        "Совет 2: Откладывайте часть доходов на сбережения.",
        "Совет 3: Покупайте товары по скидкам и распродажам."
    ]
    tip = random.choice(tips)
    await message.answer(tip)

@dp.message(F.text == "Личные финансы")
async def finances_1(message: Message, state: FSMContext):
    await state.set_state(FinancesForm.category1)
    await message.reply("Введите первую категорию расходов:")

@dp.message(FinancesForm.category1)
async def finances_2(message: Message, state: FSMContext):
    await state.update_data(category1 = message.text)
    await state.set_state(FinancesForm.expenses1)
    await message.reply("Введите расходы для категории 1:")

@dp.message(FinancesForm.expenses1)
async def finances_3(message: Message, state: FSMContext):
    await state.update_data(expenses1 = float(message.text))
    await state.set_state(FinancesForm.category2)
    await message.reply("Введите вторую категорию расходов:")

@dp.message(FinancesForm.category2)
async def finances_4(message: Message, state: FSMContext):
    await state.update_data(category2 = message.text)
    await state.set_state(FinancesForm.expenses2)
    await message.reply("Введите расходы для категории 2:")

@dp.message(FinancesForm.expenses2)
async def finances_5(message: Message, state: FSMContext):
    await state.update_data(expenses2 = float(message.text))
    await state.set_state(FinancesForm.category3)
    await message.reply("Введите третью категорию расходов:")

@dp.message(FinancesForm.category3)
async def finances_6(message: Message, state: FSMContext):
    await state.update_data(category3 = message.text)
    await state.set_state(FinancesForm.expenses3)
    await message.reply("Введите расходы для категории 3:")

@dp.message(FinancesForm.expenses3)
async def finances_7(message: Message, state: FSMContext):
    data = await state.get_data()
    telegram_id = message.from_user.id
    name = message.from_user.full_name
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute('''UPDATE users SET category1 = ?, expenses1 = ?, category2 = ?, expenses2 = ?, category3 = ?, expenses3 = ? WHERE telegram_id = ?''',
                   (data['category1'], data['expenses1'], data['category2'], data['expenses2'], data['category3'], float(message.text), telegram_id))
    conn.commit()
    await state.clear()
    cursor.execute('''SELECT * FROM users WHERE telegram_id = ?''', (telegram_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        response = f"Категории и расходы по пользователю {user[2]}:\n"
        response += f"Расходы на {user[3]} = {user[6]}\n"
        response += f"Расходы на {user[4]} = {user[7]}\n"
        response += f"Расходы на {user[5]} = {user[8]}\n"
    else:
        response = f"В базе данных нет записи по пользователю {name}"
    await message.answer(response)

# Команда для тестирования базы данных
@dp.message(Command("test_db"))
async def view_finance_data(message: Message):
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    telegram_id = message.from_user.id
    name = message.from_user.full_name
    cursor.execute('''SELECT * FROM users WHERE telegram_id = ?''', (telegram_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        response = "Запись из базы данных:\n"
        response += f"Telegram_id: {user[1]}, name = {user[2]}\n"
        response += f"Расходы по категории {user[3]} = {user[6]}\n"
        response += f"Расходы по категории {user[4]} = {user[7]}\n"
        response += f"Расходы по категории {user[5]} = {user[8]}\n"
    else:
        response = f"В базе данных нет записи по пользователю {name}"
    await message.answer(response)


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())