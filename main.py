# ---------------------------------------I M P O R T------------------------------------- #

from aiogram.utils import executor
from aiogram import types

import logging
import asyncio

from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import API_TOKEN


from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, LabeledPrice, ContentType, PreCheckoutQuery


import sqlite3 as sql

# ---------------------------------------I M P O R T------------------------------------- #


# ---------------------------------------D A T A B A S E------------------------------------- #
def sql_start():
    global conn, cur
    conn = sql.connect('products.db')
    cur = conn.cursor()
    if conn:
        print('Database is working!!!👿👿👿')
        
    conn.execute('''CREATE TABLE IF NOT EXISTS menu(product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 photo TEXT NOT NULL,
                 name CHAR(50) NOT NULL,
                 description TEXT,
                 price TEXT)''')
    
    
    conn.execute('''CREATE TABLE IF NOT EXISTS cart(order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INT NOT NULL,
                 product_id INT NOT NULL,
                 amount INT)''')
    
    
    conn.execute('''CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 number TEXT NOT NULL,
                 name TEXT NOT NULL,
                 mail TEXT NOT NULL,
                 address TEXT)''')
    conn.commit()

    
async def on_startup(_):
    sql_start()
    
# ---------------------------------------D A T A B A S E------------------------------------- #
    
    
    
    
    
# ---------------------------------------B O T------------------------------------- #   
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
# ---------------------------------------B O T------------------------------------- # 



# ---------------------------------------KEYBOARDS------------------------------------- #
kb_client_1 = KeyboardButton('/menu')
kb_client_2 = KeyboardButton('/show_cart')
kb_client_3 = KeyboardButton('/information')
kb_client = ReplyKeyboardMarkup(resize_keyboard=True)
kb_client.add(kb_client_1).add(kb_client_2).add(kb_client_3)



kb_admin_1 = KeyboardButton('/upload')
kb_admin_2 = KeyboardButton('/delete')
kb_admin_3 = KeyboardButton('/allorder')

kb_admin = ReplyKeyboardMarkup(resize_keyboard=True)
kb_admin.add(kb_admin_1).add(kb_admin_2).add(kb_admin_3)
# ---------------------------------------KEYBOARDS------------------------------------- #




# ---------------------------------------C L I E N T ------------------------------------- #

@dp.message_handler(commands=['start', 'help'])
async def start_command(message: types.Message):
    full_name = message.from_user.full_name
    await message.answer(f"Hello👋, {full_name}\nThis is the most delicious pizza🍕"+
                        "\nWe guarantee fast delivery within 30 minutes!✔️\n" +
                        "❗To view the menu, press <b>MENU</b> or write a command <b>/menu</b>❗\n" +
                        "❗To add an order, write <b>/add_cart (id_product) (amount)</b>❗\n" + 
                        "❗To see the cart, write <b>/show cart</b>❗", parse_mode="HTML", reply_markup=kb_client)
    
    
@dp.message_handler(commands=['information'])
async def info_command(message: types.Message):
    await message.answer("Adik Pizza MegaSilkway\n" + "Kabanbai batyr Ave., 62\n\n" + "Delivery and Pickup\n" +
                        "<u>Mon - Fri</u>: 10:00 — 23:00\n" + "<u>Sat - Sun</u>: 10:00 — 00:00\n\n" + "Restaurant\n" +
                        "<u>Mon - Fri</u>: 10:00 — 23:00\n" + "<u>Sat - Sun</u>: 10:00 — 00:00\n\n" + "<b>+7(776)275-41-25</b>", parse_mode="HTML")
    

@dp.message_handler(commands=['menu'])
async def menu_command(message : types.Message):
    for ret in cur.execute('SELECT * FROM menu').fetchall():
        await bot.send_photo(message.from_user.id, ret[1])
        discount_price = int(ret[4]) + 1
        await message.answer(f"<b>{ret[2]}</b>\n\ndescription:\n<i>{ret[3]}</i>\n\nprice: <s>{discount_price}</s> <b>{ret[4]}$</b>\n\ncode: {ret[0]}", parse_mode="HTML")
        

#-----------------------USER GET DATA------------------------------------

class FSMClient(StatesGroup):
    number = State()
    name = State()
    mail = State()
    address = State()

    
@dp.message_handler(commands=['add_user'], state=None)
async def add_cart(message : types.Message):
    await FSMClient.number.set()
    await message.reply('Enter the number:')
    
    
@dp.message_handler(state=FSMClient.number)
async def load_name(message : types.Message, state= FSMContext):
    async with state.proxy() as data:
        data['number'] = message.text
    await FSMClient.next()
    await message.reply('Enter the your name:')
   
    
@dp.message_handler(state=FSMClient.name)
async def load_name(message : types.Message, state= FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await FSMClient.next()
    await message.reply('Enter the your mail:')
    
    
@dp.message_handler(state=FSMClient.mail)
async def load_name(message : types.Message, state= FSMContext):
    async with state.proxy() as data:
        data['mail'] = message.text
    await FSMClient.next()
    await message.reply('Enter the your address:')
    
    
USER_ID = 1

@dp.message_handler(state=FSMClient.address)
async def load_name(message : types.Message, state= FSMContext):
    async with state.proxy() as data:
        data['address'] = message.text
        
    async with state.proxy() as data:
            number = data['number'] 
            name = data['name'] 
            global USER_ID
            USER_NAME = name
            mail = data['mail'] 
            address = data['address'] 
        
            conn.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?);", (None, number, name, mail, address))
            conn.commit()
            
            USER_ID = (conn.execute(f"SELECT user_id FROM users WHERE name='{name}'")).fetchone()[0]
            
            
            print(int(USER_ID))
    
    await state.finish()
    
    
#-----------------------USER GET DATA------------------------------------

@dp.message_handler(commands=['add_cart'])
async def add_cart(message : types.Message):
    global USER_ID
    product_id = int(message.text[10])
    amount = int(message.text[12:])
    
    conn.execute("INSERT INTO cart VALUES (?, ?, ?, ?);", (None, USER_ID, product_id, amount))
    conn.commit()
    print('Product was added!')
    

ORDER_NUMBER = 0
ALL_ORDERS = 'ALL ORDERS:\n\n'

@dp.message_handler(commands=['show_cart'])
async def add_cart(message : types.Message):
    
    global USER_ID
    global ORDER_NUMBER
    global ALL_ORDERS
    
    ALL_ORDERS = ''
    TOTAL_PRICE = 0
    
    for ret in cur.execute(f"SELECT * FROM cart WHERE user_id='{USER_ID}'").fetchall():
        product_id = ret[2]
        product_name = cur.execute(f"SELECT name FROM menu WHERE product_id='{product_id}'").fetchone()
        product_price = cur.execute(f"SELECT price FROM menu WHERE product_id='{product_id}'").fetchone()
        product_amount = int(ret[3])
        
        TOTAL_PRICE += int(product_price[0]) * product_amount 
        
        ORDER_NUMBER = int(ret[0])
        ORDER = f"order number: {ret[0]}\n" + f"*{product_name[0]} - amount: {product_amount}\n" + f"price: {product_price[0]}$\n"
        delete_order = f'write: /del_order {ret[0]}\n\n'
        board = '-' * 24 + '\n'
        ALL_ORDERS += ORDER + "\n" + delete_order + board
        
    await message.answer(f"USER ID: {USER_ID}\n\n" + ALL_ORDERS + "\nTOTAL PRICE: " + str(TOTAL_PRICE) + "$")
    
    
      
@dp.message_handler(commands='del_order')
async def state_start(message : types.Message):
    parsed_order_id = int(message.text[11:])
    print(parsed_order_id)
    conn.execute(f"DELETE FROM cart WHERE order_id={parsed_order_id}")
    conn.commit()
    await message.answer(f"№{parsed_order_id} - was deleted")
# ---------------------------------------C L I E N T ------------------------------------- #
    
    
  
    
    
#-----------------------------------------A D M I N---------------------------------------------------#

ID = None

@dp.message_handler(commands=['moderator'], is_chat_admin=True)
async def make_changes_command(message: types.Message):
    global ID 
    ID = message.from_user.id
    await bot.send_message(message.from_user.id, 'Yeah, you`re moderator\n'+
                           'I`m working👿👿👿', reply_markup=kb_admin)
    await message.delete()
    
    
@dp.message_handler(commands='allorder')
async def state_start(message : types.Message):
    parsed_msg = message.text[8:]
    for ret in cur.execute('SELECT * FROM cart').fetchall():
        order_number = ret[0]
        user_id = ret[1]
        user_number = cur.execute(f"SELECT number FROM users WHERE user_id='{user_id}").fetchone()
        user_address = cur.execute(f"SELECT address FROM users WHERE user_id='{user_id}").fetchone()
        
        
class FSMAdmin(StatesGroup):
    photo = State()
    name = State()
    description = State()
    price = State()
    

@dp.message_handler(commands='delete')
async def state_start(message : types.Message):
    parsed_msg = message.text[8:]
    conn.execute(f"DELETE from menu WHERE product_id={int(parsed_msg)}")
    conn.commit()
    

@dp.message_handler(commands='upload', state=None)
async def state_start(message : types.Message):
    # product_db.sql_start()
    if message.from_user.id == ID:
        await FSMAdmin.photo.set()
        await message.reply('Upload the photo:')
    else:
        await message.reply("Don't disturb me, ur not moderator!!!" +
                            "I`m working👿👿👿")
        
    
@dp.message_handler(content_types=['photo'], state=FSMAdmin.photo)
async def load_photo(message : types.Message, state= FSMContext):
    if message.from_user.id == ID:
    # save the data on state dictionary
        async with state.proxy() as data:
            data['photo'] = message.photo[0].file_id
        await FSMAdmin.next()
        await message.reply('Enter the name:')
    
    
@dp.message_handler(state=FSMAdmin.name)
async def load_name(message : types.Message, state= FSMContext):
    # save the data on state dictionary
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['name'] = message.text
        await FSMAdmin.next()
        await message.reply('Enter the description:')
    
    
@dp.message_handler(state=FSMAdmin.description)
async def load_description(message : types.Message, state= FSMContext):
    # save the data on state dictionary
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['description'] = message.text
        await FSMAdmin.next()
        await message.reply('Enter the price ($):')
    
    
@dp.message_handler(state=FSMAdmin.price)
async def load_price(message : types.Message, state= FSMContext):
    # save the data on state dictionary
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['price'] = message.text
        async with state.proxy() as data:
            photo_id = data['photo'] 
            name = data['name'] 
            description = data['description'] 
            price = data['price'] 
        
            conn.execute("INSERT INTO menu VALUES (?, ?, ?, ?, ?);", (None, photo_id, name, description, price))
            conn.commit()
            
            msg = "photo: " + photo_id + "\n" + "name: " + name + "\n" + description + "\n" + "price: " + price
            await message.answer(msg)
        await state.finish()
    
    
@dp.message_handler(state="*", commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_data()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Was finished..')
    
#-----------------------------------------A D M I N---------------------------------------------------#


PAYMENT_TOKEN = '401643678:TEST:504832e4-95fa-4e0b-b388-894cf95ae4d9'
price = [LabeledPrice(label='Order', amount=8000)]

# buy_button = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='payment', callback_data='new_order'))

# @dp.callback_query_handler(text='new_order')
@dp.message_handler(commands=['payment'])
async def add_cart(message : types.Message):
    await bot.send_invoice(message.chat.id,
                           title='AdikPizza',
                           description='The best pizza in ur life',
                           provider_token=PAYMENT_TOKEN,
                           currency='usd',
                           need_email='True',
                           prices=price,
                           start_parameter='example',
                           payload='some_invoice'
                           )
    await bot.send_message(5472394060, f"{ALL_ORDERS}")
 
 
@dp.pre_checkout_query_handler(lambda query: True)   
async def pre_checkout_process(pre_checkout: PreCheckoutQuery):
    await bot.answer_pre.checkout_query(pre_checkout.id, ok=True)
    
    
@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def succesful_payment(message: types.Message):
    await message.answer('SUCCESFUL PAYMENT!')



#----------------------------------R U N N I N G-----------------------------------------------------#

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
    








