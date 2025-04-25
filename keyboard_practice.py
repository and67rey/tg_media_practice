import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
import keyboards as kb
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

load_dotenv('.env')
API_TOKEN = os.getenv("API_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# /help
@dp.message(Command("help"))
async def help_handler(message: Message):
    help_text = (
        "/help - список команд с кратким описанием\n"
        "/start - меню с кнопками Привет и Пока\n"
        "/link - инлайн-кнопки Новости/Музыка/Видео с URL-ссылками\n"
        "/dynamic - инлайн-кнопка Показать больше, при нажатии на эту кнопку - инлайн-меню с кнопки Опция 1 и Опция 2"
    )
    await message.answer(help_text)

# /start
@dp.message(Command("start"))
async def start(message: Message):
   await message.answer(f'Приветики, {message.from_user.first_name}', reply_markup=kb.reply_menu)

# Обработка кнопки Привет на reply клавиатуре по команде /start
@dp.message(F.text == "Привет")
async def test_button(message: Message):
   await message.answer(f'Привет, {message.from_user.full_name}!')

# Обработка кнопки Пока на reply клавиатуре по команде /start
@dp.message(F.text == "Пока")
async def test_button(message: Message):
   await message.answer(f'До свидания, {message.from_user.full_name}!')

# /link
@dp.message(Command("link"))
async def start(message: Message):
   await message.answer('Читай новости, слушай музыку, смотри видео', reply_markup=kb.inline_menu)

# /dynamic
@dp.message(Command("dynamic"))
async def dynamic_start(message: Message):
    await message.answer("Выберите действие:", reply_markup=kb.dynamic_menu)

# Обработка кнопки "Показать больше"
@dp.callback_query(F.data == "show_more")
async def show_more_options(callback: CallbackQuery):
    await callback.message.edit_text("Выберите опцию:", reply_markup=kb.options_menu)
    await callback.answer()

# Обработка кнопки "Опция 1"
@dp.callback_query(F.data == "option_1")
async def option_1(callback: CallbackQuery):
    await callback.message.answer("Вы выбрали Опция 1")
    await callback.answer()

# Обработка кнопки "Опция 2"
@dp.callback_query(F.data == "option_2")
async def option_2(callback: CallbackQuery):
    await callback.message.answer("Вы выбрали Опция 2")
    await callback.answer()


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
