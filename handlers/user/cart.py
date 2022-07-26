from keyboards.inline.categories import categories_markup
import logging
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.inline.products_from_cart import product_markup, product_cb
from keyboards.inline.products_from_catalog import back_to_menu
from aiogram.utils.callback_data import CallbackData
from aiogram.types.chat import ChatActions
from data.config import ADMINS, CHANNELS
from keyboards.default.markups import *
from states import CheckoutState
from loader import dp, db, bot
from filters import IsUser
from aiogram import types
from .menu import cart, catalog
from keyboards.inline.confirm import confirmation_keyboard




@dp.message_handler(IsUser(), text=cart)
async def process_cart(message: Message, state: FSMContext):

    cart_data = db.fetchall(
        'SELECT * FROM cart WHERE cid=?', (message.chat.id,))

    if len(cart_data) == 0:

        await message.answer('Sizning savatingiz bo\'sh')

    else:

        await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
        async with state.proxy() as data:
            data['products'] = {}

        order_cost = 0

        for _, idx, count_in_cart in cart_data:

            product = db.fetchone('SELECT * FROM products WHERE idx=?', (idx,))

            if product == None:

                db.query('DELETE FROM cart WHERE idx=?', (idx,))

            else:
                global image
                _, title, body, image, price, _ = product
                order_cost += price

                async with state.proxy() as data:
                    data['products'][idx] = [title, price, count_in_cart]

                markup = product_markup(idx, count_in_cart)
                text = f'<b>{title}</b>\n\n{body}\n\nБахоси: {price}Сум.'

                await message.answer_photo(photo=image,
                                           caption=text,
                                           reply_markup=markup)

        if order_cost != 0:
            markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            markup.add('📦 Буюртма бериш')
            markup.add('🔙 Orqaga')
            
            await message.answer('Хисоб-китоб киламизми?',
                                 reply_markup=markup)


@dp.callback_query_handler(IsUser(), product_cb.filter(action='count'))
@dp.callback_query_handler(IsUser(), product_cb.filter(action='increase'))
@dp.callback_query_handler(IsUser(), product_cb.filter(action='decrease'))
async def product_callback_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):

    idx = callback_data['id']
    action = callback_data['action']

    if 'count' == action:

        async with state.proxy() as data:

            if 'products' not in data.keys():

                await process_cart(query.message, state)

            else:

                await query.answer('Микдор - ' + data['products'][idx][2])

    else:

        async with state.proxy() as data:

            if 'products' not in data.keys():

                await process_cart(query.message, state)

            else:

                data['products'][idx][2] += 1 if 'increase' == action else -1
                count_in_cart = data['products'][idx][2]

                if count_in_cart == 0:

                    db.query('''DELETE FROM cart
                    WHERE cid = ? AND idx = ?''', (query.message.chat.id, idx))

                    await query.message.delete()
                else:

                    db.query('''UPDATE cart 
                    SET quantity = ? 
                    WHERE cid = ? AND idx = ?''', (count_in_cart, query.message.chat.id, idx))

                    await query.message.edit_reply_markup(product_markup(idx, count_in_cart))


@dp.message_handler(IsUser(), text='📦 Буюртма бериш')
# @dp.callback_query_handler(IsUser(), product_cb.filter(action='order_p'))
async def process_checkout(message: Message, state: FSMContext):

    await CheckoutState.check_cart.set()
    await checkout(message, state)


async def checkout(message, state):
    global check_admin
    answer = ''
    total_price = 0

    async with state.proxy() as data:

        for title, price, count_in_cart in data['products'].values():

            tp = count_in_cart * price
            answer += f'<b>{title}</b> * {count_in_cart}шт. = {tp}so\'m\n'
            total_price += tp

    await message.answer(f'{answer}\nБуюртманинг умумий суммаси: {total_price}so\'m.',
                         reply_markup=check_markup())
    check_admin = f'{answer}\nБуюртманинг умумий суммаси: {total_price}so\'m.\n'


@dp.message_handler(IsUser(), lambda message: message.text not in [all_right_message, back_message], state=CheckoutState.check_cart)
async def process_check_cart_invalid(message: Message):
    await message.reply('Бундай вариант бўлмаган.')


@dp.message_handler(IsUser(), text=back_message, state=CheckoutState.check_cart)
async def process_check_cart_back(message: Message, state: FSMContext):
    await state.finish()
    await process_cart(message, state)


@dp.message_handler(IsUser(), text=all_right_message, state=CheckoutState.check_cart)
async def process_check_cart_all_right(message: Message, state: FSMContext):
    await CheckoutState.next()
    await message.answer('ЖАЙХУН ГУЛШАНИГА БУЮРТМА БЕРИШ УЧУН САВОЛЛАРГА ЖАВОБ БЕРИНГ...❓❓❓❓❓')
    await message.answer('<b>🫶 Исмингизни киритинг.</b>',
                         reply_markup=back_markup())


@dp.message_handler(IsUser(), text=back_message, state=CheckoutState.name)
async def process_name_back(message: Message, state: FSMContext):
    await CheckoutState.check_cart.set()
    await checkout(message, state)


@dp.message_handler(IsUser(), state=CheckoutState.name)
async def process_name(message: Message, state: FSMContext):

    async with state.proxy() as data:

        data['name'] = message.text

        if 'address' in data.keys():

            await confirm(message)
            await CheckoutState.confirm.set()

        else:

            await CheckoutState.next()
            # await message.answer('Яшаш манзилингизни толик киритинг.( шахар, туман, кишлок, махала, коча, уй сони. )',
            #                      reply_markup=back_markup())
            await message.answer('<b>🎂 ТУҒИЛГAН КУН ҚAЧОН?</b>',
                                 reply_markup=back_markup())


@dp.message_handler(IsUser(), state=CheckoutState.when_bday)
async def process_when_bday(message: Message, state: FSMContext):

    async with state.proxy() as data:
        data['when_bday'] = message.text

    await CheckoutState.next()
    await message.answer('ТУҒИЛГAН КУН ЕГAСИНИНГ МAНЗИЛИ ҚAЙЕРДA?\n\nЯшаш манзилингизни толик киритинг.( шахар, туман, кишлок, махала, коча, уй сони. )',
                         reply_markup=back_markup())


@dp.message_handler(IsUser(), text=back_message, state=CheckoutState.address)
async def process_address_back(message: Message, state: FSMContext):

    async with state.proxy() as data:

        await message.answer('Исмингизни озгартиринг <b>' + data['name'] + '</b>?',
                             reply_markup=back_markup())

    await CheckoutState.name.set()


@dp.message_handler(IsUser(), state=CheckoutState.address)
async def process_address(message: Message, state: FSMContext):

    async with state.proxy() as data:
        data['address'] = message.text

    await CheckoutState.next()
    # await message.answer('Телефон рақамингизни киритинг.',
    #                      reply_markup=back_markup())
    await message.answer('<b>💳 ТЎЛОВ ТУРИ \ ПЛAСТИК ЙОКИ НAҚТ</b>')


@dp.message_handler(IsUser(), state=CheckoutState.cash_or_online)
async def process_cash_or_online(message: Message, state: FSMContext):

    async with state.proxy() as data:
        data['cash_or_online'] = message.text

    await CheckoutState.next()
    # await message.answer('Телефон рақамингизни киритинг.',
    #                      reply_markup=back_markup())
    await message.answer('<b>📞 Телефон рақамингизни киритинг.</b>')

@dp.message_handler(IsUser(), state=CheckoutState.phone)
async def process_phone(message: Message, state: FSMContext):

    async with state.proxy() as data:
        data['phone'] = message.text

    await CheckoutState.next()
    msg = f"❗️❗️❗️ <b>Диккат киламиз!</b>\n\n"
    msg += f"<b>Агарда сиз чет эл дан уйингизга буюртма бермокчи болсангиз:</b>\n"
    msg += f"GPS('местоположение)  учик холда телефон оркали харитадан Узбекистандаги уйингизни \"локация\"сини юборинг.\n\n"
    msg += f'<b>Йоки "Узб"да болсангиз:</b>'
    msg += f'Телеграм оркали  GPS ( местоположение) ни ëкиб турар жойингизни локатсиясини ташанг.\n\n'
    msg += f'Акс холда нотогри локатсия ташаб юборасиз!!!'
        

    await message.answer(msg, reply_markup=geo())


@dp.message_handler(IsUser(), state=CheckoutState.location, content_types=['location'])
async def process_locate(message: types.Message, state: FSMContext):

    # if message.location is not None:
    #     print(message.location)
    # print("latitude: %s; longitude: %s" % (message.location.latitude, message.location.longitude))
    #     await message.answer("https://www.google.com/search?q=%s+%s" % (message.location.latitude, message.location.longitude))

    # if message.location is not None:

    async with state.proxy() as data:
        data['location'] = ("https://www.google.com/search?q=%s+%s" %
                            (message.location.latitude, message.location.longitude))

    # await confirm(message)
    await CheckoutState.next()
    await message.answer('<b>🕔 СОAТ НЕЧAГA БОРИШ КЕРAК?</b>')

    # else:

    #     await confirm(message)
    #     await CheckoutState.next()


@dp.message_handler(IsUser(), state=CheckoutState.when_to_go)
async def process_when_to_go(message: Message, state: FSMContext):

    async with state.proxy() as data:
        data['when_to_go'] = message.text

    await CheckoutState.next()

    await message.answer('<b>👤 ТУҒИЛГAН КУН ЭГAСИНИНГ ИСМИ?</b>')


@dp.message_handler(IsUser(), state=CheckoutState.name_person_bday)
async def process_name_person_bday(message: Message, state: FSMContext):

    async with state.proxy() as data:
        data['name_person_bday'] = message.text

    await CheckoutState.next()

    await message.answer('<b>🎁 КИМНИНГ НОМИДAН ТAБРИКЛAЙМИЗ?</b>')


@dp.message_handler(IsUser(), state=CheckoutState.kimning_nomidan)
async def process_kimning_nomidan(message: Message, state: FSMContext):

    async with state.proxy() as data:
        data['kimning_nomidan'] = message.text

    await CheckoutState.next()
    await message.answer('<b>☎️ БИЗНИ КУТИБ ОЛAДИГAН ИНСОННИНГ ТЕЛЕФОН РAҚAМИ ?</b>')
    

@dp.message_handler(IsUser(), state=CheckoutState.bizni_kutibol)
async def process_bizni_kutibol(message: Message, state: FSMContext):

    async with state.proxy() as data:
        data['bizni_kutibol'] = message.text

    await CheckoutState.next()
    await confirm(message)


async def confirm(message):

    await message.answer('<b>Ҳаммаси тўғри эканлигига ишонч ҳосил қилинг ва буюртмани тасдиқланг.</b>',
                         reply_markup=confirm_markup())


@dp.message_handler(IsUser(), lambda message: message.text not in [confirm_message, back_message], state=CheckoutState.confirm)
async def process_confirm_invalid(message: Message):
    await message.reply('Бундай вариант бўлмаган.')


@dp.message_handler(IsUser(), text=back_message, state=CheckoutState.confirm)
async def process_confirm(message: Message, state: FSMContext):

    await CheckoutState.address.set()

    async with state.proxy() as data:
        await message.answer('Манзилни озгартириш <b>' + data['address'] + '</b>?',
                             reply_markup=back_markup())


@dp.message_handler(IsUser(), text=confirm_message, state=CheckoutState.confirm)
async def process_confirm(message: Message, state: FSMContext):

    enough_money = True  # enough money on the balance sheet
    markup = ReplyKeyboardRemove()
    markup_back = back_to_menu()
    markup_new = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)

    markup_new.add(catalog, cart)

    if enough_money:

        logging.info('Deal was made.')

        async with state.proxy() as data:

            cid = message.chat.id
            products = [idx + '=' + str(quantity)
                        for idx, quantity in db.fetchall('''SELECT idx, quantity FROM cart
            WHERE cid=?''', (cid,))]  # idx=quantity

            db.query('INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                     (cid, data['name'], data['when_bday'], data['address'], data['cash_or_online'],
                      data['phone'], data['location'], data['when_to_go'], data['name_person_bday'], data['kimning_nomidan'], data['bizni_kutibol'], ' '.join(products)))

            db.query('DELETE FROM cart WHERE cid=?', (cid,))

            # msg = f'🚀\nИсм: <b>' + data['name'] + '</b>\nМанзил: <b>' + data['location'] + '</b>'

            await message.answer(f'ОК! Сизнинг буюртмангиз қабул қилинди, яқин орада сиз билан админ бўгланади 🚀')

            username = message.from_user.username

            msg = f"❗️❗️❗️ <b>Sizning buyurmangiz: @{username}</b>\n\n"
            msg += f"<i>Ism:</i> <b>{data['name']}</b>\n\n"
            msg += f"<i>Telefon raqam:</i> <b>{data['phone']}</b>\n\n"
            msg += f"<i>ТУҒИЛГAН КУН ЕГAСИНИНГ МAНЗИЛИ ҚAЙЕРДA?:</i> <b>{data['address']}</b>\n\n"
            msg += f"<i>ТЎЛОВ ТУРИ \ ПЛAСТИК ЙОКИ НAҚТ:</i> <b>{data['cash_or_online']}</b>\n\n"
            msg += f"<i>СОAТ НЕЧAГA БОРИШ КЕРAК?:</i> <b>{data['when_to_go']}</b>\n\n"
            msg += f"<i>ТУҒИЛГAН КУН ЭГAСИНИНГ ИСМИ?:</i> <b>{data['name_person_bday']}</b>\n\n"
            msg += f"<i>КИМНИНГ НОМИДAН ТAБРИКЛAЙМИЗ?:</i> <b>{data['kimning_nomidan']}</b>\n\n"
            msg += f"<i>БИЗНИ КУТИБ ОЛAДИГAН ИНСОННИНГ ТЕЛЕФОН РAҚAМИ ?:</i> <b>{data['bizni_kutibol']}</b>\n\n"
            msg += f"<i>GEO-Manzil:</i> <b>{data['location']}</b>\n\n"

            await message.answer(f'{check_admin}\n {"-"*70}\n\n{msg}', reply_markup=markup)

            for i in ADMINS:
                await bot.send_message(i, f'{check_admin}\n {"-"*70}\n\n{msg}', reply_markup=confirmation_keyboard)
            
            await message.answer("Xaridingiz uchun raxmat 😎😎😎", reply_markup=markup_new)
            await message.answer("<b>Келинг, совғангизни бирга танлаймиз\n✌️</b>",reply_markup=categories_markup())
            

            await state.finish()

    else:

        await message.answer('Ҳисобингизда пул етарли эмас. Балансингизни толдиринг!',
                             reply_markup=markup)


# @dp.message_handler(text="confirm")


@dp.callback_query_handler(text='confirm_a')
async def confirm_post(call: CallbackQuery):
    message = await call.message.edit_reply_markup()
    await message.send_copy(chat_id=CHANNELS[0])
    # await state.finish()
# @dp.message_handler(text="cancel")


@dp.callback_query_handler(text='cancel_a')
async def cancel_post(call: CallbackQuery):
    # await call.message.delete()
    await call.message.answer("Bekor qilindi")
    # await state.finish()




