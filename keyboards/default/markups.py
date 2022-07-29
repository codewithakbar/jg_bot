from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from handlers.user.menu import catalog

back_message = '👈 Оркага'
confirm_message = '✅ Буюртмани тастиклаш'
all_right_message = '✅ Хаммаси тогри'
cancel_message = '🚫 Бекор килиш'


def catalog_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(catalog)

def confirm_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(confirm_message)
    markup.add(back_message)

    return markup

def back_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(back_message)

    return markup

def check_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row(back_message, all_right_message)

    return markup

def submit_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row(cancel_message, all_right_message)

    return markup


def geo():
    keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_geo = KeyboardButton(
        text="GPS-манзил юбориш", request_location=True)
    keyboard.add(button_geo)
    return keyboard
