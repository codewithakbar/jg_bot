from loader import dp, bot
from aiogram.types import CallbackQuery
from aiogram import types
from aiogram.dispatcher import FSMContext
from data.config import ADMINS, CHANNELS
from keyboards.inline.products_from_catalog import back_to_menu
from keyboards.default.markups import confirm_markup
from states.checkout_state import CheckoutState


@dp.callback_query_handler(text='✅ Буюртмани тастиклаш', state=CheckoutState.confirm)
async def confirm_post(call: CallbackQuery, state: FSMContext):
    # Ma'lumotlarni qayta o'qiymiz
    data = await state.get_data()
    title = data.get('title')
    desc = data.get('desc')
    price = data.get('price')
    phone = data.get('phone')
    address = data.get('address')
    image = data.get('image')

    msg = f"❗️❗️❗️ <b>Mahsulot sotiladi</b>\n\n"
    msg += f"Nomi: {title}\n"
    msg += f"Batafsil: {desc}\n"
    msg += f"Narxi: {price}\n"
    msg += f"Tel raqam: {phone}\n"
    msg += f"Manzil: {address}\n"
    await call.answer("Adminga jo'natildi", show_alert=True)
    for i in ADMINS:
        await bot.send_photo(i, image, caption=msg, reply_markup=confirm_markup())
    await call.message.edit_reply_markup()
    await state.finish()


@dp.callback_query_handler(text='cancel', state=CheckoutState.confirm)
async def cancel_post(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer("Bekor qilindi", reply_markup=back_to_menu)
    await state.finish()


@dp.callback_query_handler(text='admin_confirm')
async def confirm_post(call: CallbackQuery):
    message = await call.message.edit_reply_markup()
    await message.send_copy(chat_id=CHANNELS[0])


@dp.callback_query_handler(text='admin_cancel')
async def cancel_post(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer("Bekor qilindi")
