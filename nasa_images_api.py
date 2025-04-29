import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import requests
import random
from dotenv import load_dotenv

# URL для получения изображения NASA
NASA_IMAGES_URL = 'https://images-api.nasa.gov/search'

load_dotenv('.env')
API_TOKEN = os.getenv("API_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

user_settings = {}

# Инлайн-клавиатура для выбора режима подачи описания
desc_inline_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="С описанием", callback_data="description_on"),
    InlineKeyboardButton(text="Без описания", callback_data="description_off")]
])

# Команда /start - приветственное сообщение и установка языка по умолчанию
@dp.message(Command("start"))
async def start_handler(message: Message):
    start_text = (
        "👋 Привет! Я - ваш проводник в удивительный и прекрасный мир космоса!\n"
        "Введите запрос на английском языке - и получите случайное изображение NASA по этой теме"
    )
    await message.answer(start_text)

# Команда /help - описание работы с ботом
@dp.message(Command("help"))
async def send_help(message: Message):
    help_text = (
        "❓ Вот что я умею:\n"
        "/start - Приветственное сообщение\n"
        "/help - Краткая информация о боте и его функциях\n"
        "/desc - Выбор режима вывода описания для изображений\n"
        "Введите слово на английском языке - и получите случайное изображение NASA по этой теме"
    )
    await message.answer(help_text)

# Команда /desc
@dp.message(Command("desc"))
async def send_desc(message: Message):
   await message.answer('Выберите режим подачи описания', reply_markup=desc_inline_menu)

# Обработка кнопки "С описанием"
@dp.callback_query(F.data == "description_on")
async def desc_on(callback: CallbackQuery):
    user_settings[callback.from_user.id] = True
    await callback.message.answer("Вы выбрали режим с описанием")
    await callback.answer()

# Обработка кнопки "Без описания"
@dp.callback_query(F.data == "description_off")
async def desc_off(callback: CallbackQuery):
    user_settings[callback.from_user.id] = False
    await callback.message.answer("Вы выбрали режим без описания")
    await callback.answer()

@dp.message()
async def send_image_word(message: Message):
   user_id = message.from_user.id
   # Устанавливаем True по умолчанию
   show_desc = user_settings.get(user_id, True)
   # Если пользователь еще не внесен в словарь — добавим
   if user_id not in user_settings:
       user_settings[user_id] = True

   query = message.text
   query_params = {"q": query, "media_type": 'image'}
   response = requests.get(NASA_IMAGES_URL, params=query_params)
   if response.status_code == 200:
       res_json = response.json()
       items = res_json['collection']['items']
       if len(items) > 0:
           n = random.randint(0, len(items) - 1)
           image_url = res_json['collection']['items'][n]['links'][0]['href']
           title = res_json['collection']['items'][n]['data'][0]['title']
           description = res_json['collection']['items'][n]['data'][0]['description']
           if len(items) > 1:
               await message.answer(f'Случайно выбранное изображение из {len(items)} найденных по запросу\n')
           await message.answer_photo(photo=image_url, caption=f'<b>Название</b>: {title}\n', parse_mode='HTML')
           if show_desc:
              await message.answer(f'<b>Описание</b>:\n{description}', parse_mode='HTML')
       else:
           await message.answer("Ни одно изображение по запросу не найдено. Попробуйте еще раз.")
   else:
       await message.answer("При выполнении запроса произошел сбой. Попробуйте еще раз")


async def main():
   await dp.start_polling(bot)

if __name__ == '__main__':
   asyncio.run(main())