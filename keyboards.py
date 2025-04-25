from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# reply-клавиатура
reply_menu = ReplyKeyboardMarkup(keyboard=[
   [KeyboardButton(text="Привет"), KeyboardButton(text="Пока")]
], resize_keyboard=True)

# inline-клавиатура для новостей, музыки и видео
inline_menu = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text="Новости", url='https://www.rbc.ru/'),
   InlineKeyboardButton(text="Музыка", url='https://rutube.ru/video/fb80d24f0bd1096cefe21d778e42cb69/'),
   InlineKeyboardButton(text="Видео", url='https://rutube.ru/video/64212744017c3c5108ce6cd0be5c1d5f/')]
])

# Динамическая inline-клавиатура
dynamic_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Показать больше", callback_data="show_more")]
])

# Клавиатура с двумя опциями
options_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Опция 1", callback_data="option_1"),
    InlineKeyboardButton(text="Опция 2", callback_data="option_2")]
])
