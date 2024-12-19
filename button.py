from aiogram.types import ReplyKeyboardMarkup, KeyboardButton # noqa
from aiogram import types

all = [ # noqa
    [types.KeyboardButton(text="✈️Foydalanuvchilarga ma'lumot yuborish"), types.KeyboardButton(text="🚫Band qilingan joylarni ko'rish")], # noqa
    [types.KeyboardButton(text="🆕Menuga taom qo'shish"), types.KeyboardButton(text="✂️Xonani o'chirish:")] # noqa
]
button = types.ReplyKeyboardMarkup(keyboard=all, resize_keyboard=True, input_field_placeholder="Tanlang:") # noqa

sms = [
    [types.KeyboardButton(text="📨EFendiga yozish")], # noqa
]
sms2 = types.ReplyKeyboardMarkup(keyboard=sms, resize_keyboard=True) # noqa


place = [
    [types.KeyboardButton(text="🏠 1"), types.KeyboardButton(text="🏠 2"), types.KeyboardButton(text="🏠 3"), types.KeyboardButton(text="🏠 4")],
    [types.KeyboardButton(text="🏠 5"), types.KeyboardButton(text="🏠 6"), types.KeyboardButton(text="🏠 7"), types.KeyboardButton(text="🏠 8")],
    [types.KeyboardButton(text="🏠 9"), types.KeyboardButton(text="🏠 10")],
    [types.KeyboardButton(text="🔙Orqaga qaytish")]
]
place2 = types.ReplyKeyboardMarkup(keyboard=place, resize_keyboard=True, one_time_keyboard=True)