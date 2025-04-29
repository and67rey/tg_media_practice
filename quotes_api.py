import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
import requests
from deep_translator import GoogleTranslator
from dotenv import load_dotenv

# URL для получения случайной цитаты
RANDOM_QUOTE_URL = 'https://zenquotes.io/api/random'

load_dotenv('.env')
API_TOKEN = os.getenv("API_TOKEN")
QUOTES_TOKEN = os.getenv("ZEN_QUOTES_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Словарь для хранения выбранного языка пользователей
user_language = {}

# Функция для получения случайной цитаты
def get_random_quote():
    try:
        response = requests.get(RANDOM_QUOTE_URL)
        if response.status_code == 200:
            data = response.json()
            quote = f"{data[0]['q']} — {data[0]['a']}"
            return quote
        else:
            return "Не удалось получить цитату, попробуйте позже."
    except Exception as e:
        print(f"Ошибка при получении цитаты: {e}")
        return "Произошла ошибка при получении цитаты."


# Функция для перевода цитаты на русский язык
def translate_to_russian(text):
    try:
        translated = GoogleTranslator(source='en', target='ru').translate(text)
        return translated
    except Exception as e:
        print(f"Ошибка при переводе: {e}")
        return "Не удалось перевести цитату."


# Команда /start - приветственное сообщение и установка языка по умолчанию
@dp.message(Command("start"))
async def start_handler(message: Message):
    user_id = message.from_user.id
    user_language[user_id] = 'rus'  # Устанавливаем язык по умолчанию на русский
    start_text = (
        "👋 Привет! Я - ваш мотивационный бот! Я могу помочь вам начать день с вдохновения.\n"
        "Используйте команду /motivate, чтобы получить случайную мотивирующую цитату.\n"
        "Для изменения языка используйте команды /english и /russian."
    )
    await message.answer(start_text)

# Команда /help - описание работы с ботом
@dp.message(Command("help"))
async def send_help(message: Message):
    help_text = (
        "❓ Вот что я умею:\n"
        "/start - Приветственное сообщение и установка русского языка по умолчанию\n"
        "/help - Краткая информация о боте и его функциях\n"
        "/motivate - Получите случайную мотивирующую цитату\n"
        "/english - Переключение на английский язык\n"
        "/russian - Переключение на русский язык"
    )
    await message.answer(help_text)

# Команда /english - переключение на английский язык
@dp.message(Command("english"))
async def set_english(message: Message):
    user_id = message.from_user.id
    user_language[user_id] = 'eng'
    await message.answer("🌍 Язык установлен на английский. Теперь цитаты будут на английском языке.")

# Команда /russian - переключение на русский язык
@dp.message(Command("russian"))
async def set_russian(message: Message):
    user_id = message.from_user.id
    user_language[user_id] = 'rus'
    await message.answer("🌍 Язык установлен на русский. Теперь цитаты будут на русском языке.")

# Команда /motivate - отправка мотивирующей цитаты в зависимости от выбранного языка
@dp.message(Command("motivate"))
async def send_motivation(message: Message):
    user_id = message.from_user.id
    quote = get_random_quote()
    # Проверяем выбранный язык пользователя
    if user_language.get(user_id) == 'rus':
        # Переводим цитату на русский
        quote = translate_to_russian(quote)
    await message.answer(quote)

async def main():
   await dp.start_polling(bot)

if __name__ == '__main__':
   asyncio.run(main())