import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging
import sqlite3
from dotenv import load_dotenv

class Form(StatesGroup):
    name = State()
    age = State()
    grade = State()

def init_db():
    conn = sqlite3.connect('school_data.db')
    cur = conn.cursor()
    cur.execute('''
	CREATE TABLE IF NOT EXISTS students (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT NOT NULL,
	age INTEGER NOT NULL,
	grade TEXT NOT NULL)
	''')
    conn.commit()
    conn.close()

logging.basicConfig(level=logging.INFO)

init_db()

load_dotenv('.env')
API_TOKEN = os.getenv("API_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer("Привет! Как тебя зовут?")
    await state.set_state(Form.name)

# /help
@dp.message(Command("help"))
async def help_handler(message: Message):
    help_text = (
        "Бот поддерживает команды /start и /help\n"
        "Бот просит пользователя ввести его имя, возраст и класс обучения "
        "и сохраняет полученную информацию в базу данных."
    )
    await message.answer(help_text)

@dp.message(Form.name)
async def name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Сколько тебе лет?")
    await state.set_state(Form.age)

@dp.message(Form.age)
async def age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("В каком классе ты учишься?")
    await state.set_state(Form.grade)

@dp.message(Form.grade)
async def grade(message: Message, state:FSMContext):
    await state.update_data(grade=message.text)
    student_data = await state.get_data()
    conn = sqlite3.connect('school_data.db')
    cur = conn.cursor()
    cur.execute('''
       INSERT INTO students (name, age, grade) VALUES (?, ?, ?)''',
                (student_data['name'], student_data['age'], student_data['grade']))
    conn.commit()
    conn.close()
    await message.answer("Информация сохранена в базе данных")
    await state.clear()

# Команда для тестирования базы данных
@dp.message(Command("test_db"))
async def view_school_data(message: Message):
    conn = sqlite3.connect('school_data.db')
    cur = conn.cursor()
    cur.execute("SELECT id, name, age, grade FROM students")
    rows = cur.fetchall()
    conn.close()
    if rows:
        response = "Записи из базы данных:\n"
        for row in rows:
            response += f"{row[0]}. Имя: {row[1]}, возраст = {row[2]}, класс {row[3]}\n"
    else:
        response = "База данных пуста, в ней нет информации."
    await message.answer(response)


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())