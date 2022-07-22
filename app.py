
import os
import handlers
import logging
import filters
from data import config
from loader import dp, db, bot
from aiogram import executor, types
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from handlers.user.menu import catalog, balance, cart, delivery_status

filters.setup(dp)

WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.environ.get("PORT", 5000))
user_message = 'user'
admin_message = 'admin'


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):

    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)

    markup.add(catalog, cart)

    await message.answer('''<b>Salom!</b> 👋

🤖 <b>Men savdo-sotik boyicha Jayhun Gulshani savdo botiman.</b>

❓ <b>Muommo xosil boldimi? Muammo emas! /sos buyrug'i admin bilan bog'lanishga yordam beradi.</b>

🤝 <b>@JAYHUNGULSHANI BILAN UNUTILMAS ONLARINGIZNI TARIXGA MUHIRLANG</b>''', reply_markup=markup)


@dp.message_handler(text=user_message)
async def user_mode(message: types.Message):

    cid = message.chat.id
    if cid in config.ADMINS:
        config.ADMINS.remove(cid)

    await message.answer('Включен пользовательский режим. /start', reply_markup=ReplyKeyboardRemove())


@dp.message_handler(text=admin_message)
async def admin_mode(message: types.Message):

    cid = message.chat.id
    if cid not in config.ADMINS:
        config.ADMINS.append(cid)

    await message.answer('Включен админский режим. /menu', reply_markup=ReplyKeyboardRemove())


async def on_startup(dp):
    logging.basicConfig(level=logging.INFO)
    # db.create_tables()

    await bot.delete_webhook()
    await bot.set_webhook(config.WEBHOOK_URL)


async def on_shutdown():
    logging.warning("Shutting down..")
    await bot.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()
    logging.warning("Bot down")


if __name__ == '__main__':

    if "HEROKU" in list(os.environ.keys()):

        executor.start_webhook(
            dispatcher=dp,
            webhook_path=config.WEBHOOK_PATH,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT,
        )

    else:

        executor.start_polling(dp, on_startup=on_startup, skip_updates=False)
