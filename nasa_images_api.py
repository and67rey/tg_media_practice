import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
import requests
import random
from dotenv import load_dotenv

# URL для получения изображения NASA
NASA_IMAGES_URL = 'https://images-api.nasa.gov/search'

load_dotenv('.env')
API_TOKEN = os.getenv("API_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


# Команда /start - приветственное сообщение и установка языка по умолчанию
@dp.message(Command("start"))
async def start_handler(message: Message):
    start_text = (
        "👋 Привет! Я - ваш проводник в удивительный и прекрасный мир космоса!\n"
        "Введите слово на английском языке - и получите случайное изображение NASA по этой теме"
    )
    await message.answer(start_text)

# Команда /help - описание работы с ботом
@dp.message(Command("help"))
async def send_help(message: Message):
    help_text = (
        "❓ Вот что я умею:\n"
        "/start - Приветственное сообщение\n"
        "/help - Краткая информация о боте и его функциях\n"
        "Введите слово на английском языке - и получите случайное изображение NASA по этой теме"
    )
    await message.answer(help_text)


@dp.message()
async def send_image_word(message: Message):
   query = message.text
   query_params = {"q": query}
   response = requests.get(NASA_IMAGES_URL, params=query_params)
   if response.status_code == 200:
       res_json = response.json()
       items = res_json['collection']['items']
       if len(items) > 0:
           n = random.randint(0, len(items) - 1)
           image_url = res_json['collection']['items'][n]['links'][0]['href']
           title = res_json['collection']['items'][n]['data'][0]['title']
           await message.answer_photo(photo=image_url, caption=f"{title}")
       else:
           await message.answer("Ни одно изображение по запросу не найдено. Попробуйте еще раз.")
   else:
       await message.answer("При выполнении запроса произошел сбой. Попробуйте еще раз")


async def main():
   await dp.start_polling(bot)

if __name__ == '__main__':
   asyncio.run(main())