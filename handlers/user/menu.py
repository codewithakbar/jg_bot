
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup
from filters import IsAdmin, IsUser
from keyboards.inline.categories import categories_markup
from loader import dp

catalog = '🛍️ Каталог'
balance = '💰 Баланс'
cart = '🛒 Сават'
delivery_status = '🚚 Буюртма холати'

settings = '⚙️ Katalog so\'zlamalari'
orders = '🚚 Zaqazlar'
questions = '❓ Savollar'


@dp.message_handler(IsAdmin(), commands='menu')
async def admin_menu(message: Message):
    markup = ReplyKeyboardMarkup(selective=True)
    markup.add(settings)
    # markup.add(questions, orders)

    await message.answer('Меню', reply_markup=markup)


@dp.message_handler(IsUser(), commands='menu')
async def user_menu(message: Message):
    markup = ReplyKeyboardMarkup(selective=True)
    markup.add(catalog)
    markup.add(balance, cart)
    markup.add(delivery_status)

    await message.answer('Меню', reply_markup=markup)


@dp.callback_query_handler(text='back')
async def back_post(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer('''<b>Келинг, совғангизни бирга танлаймиз\n✌️</b>''', reply_markup=categories_markup())
