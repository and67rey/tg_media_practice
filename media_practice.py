import os
import asyncio
from aiogram import Bot, Dispatcher, Router, types
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from aiogram import F
from gtts import gTTS
from deep_translator import GoogleTranslator
from datetime import datetime
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

load_dotenv('.env')
API_TOKEN = os.getenv("API_TOKEN")

# Создание необходимых папок
os.makedirs("img", exist_ok=True)
os.makedirs("voice", exist_ok=True)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# /start
@dp.message(Command("start"))
async def start_handler(message: Message):
    start_text = (
        "Привет! Я бот, который:\n"
        "- сохраняет отправленные изображения\n"
        "- озвучивает дату и время\n"
        "- переводит текст на английский язык\n"
        "Введи /help для списка команд."
    )
    await message.answer(start_text)

# /help
@dp.message(Command("help"))
async def help_handler(message: Message):
    help_text = (
        "/start - приветственное сообщение\n"
        "/help - список команд\n"
        "/date - голосовое сообщение с текущей датой\n"
        "/time - голосовое сообщение с текущим временем"
    )
    await message.answer(help_text)

# /date
@dp.message(Command("date"))
async def date_handler(message: Message):
    now = datetime.now()
    date_text = now.strftime("Сегодня %d %B %Y года")
    tts = gTTS(text=date_text, lang='ru')
    file_path = f"voice/date_{message.from_user.id}.mp3"
    tts.save(file_path)
    await message.answer_voice(voice=FSInputFile(file_path))

# /time
@dp.message(Command("time"))
async def time_handler(message: Message):
    now = datetime.now()
    time_text = now.strftime("Сейчас %H часов %M минут")
    tts = gTTS(text=time_text, lang='ru')
    file_path = f"voice/time_{message.from_user.id}.mp3"
    tts.save(file_path)
    await message.answer_voice(voice=FSInputFile(file_path))

# Обработка фото
@dp.message(F.photo)
async def photo_handler(message: Message):
    photo = message.photo[-1]
    file_id = photo.file_id
    file = await message.bot.get_file(file_id)
    file_path = f"img/{file_id}.jpg"
    await message.bot.download_file(file.file_path, file_path)
    await message.answer("Фото сохранено!")

# Перевод текста
@dp.message()
async def translate_handler(message: Message):
    translated = GoogleTranslator(source='auto', target='en').translate(message.text)
    await message.answer(f"Перевод: {translated}")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())