import hashlib
from aiogram import types, Dispatcher
from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from create_bot import dp, bot, connection
from keyboards.balance import get_balance_markup, correctly_markup, payout_markup, returne_balance_chips_markup, returne_balance_cash_markup, buy_chips_markup, transfer_money_markup, withdraw_money_markup, currency_markup
from keyboards.menu import back_main_menu_markup, mein_menu_markup
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
import requests

class ReplenishmentCashCurrency(StatesGroup):
    start = State()

class ReplenishmentCashValue(StatesGroup):
    start = State()

class PayoutSistem(StatesGroup):
    start = State()
    
class PayoutСurrency(StatesGroup):
    start = State()
    
class PayoutValue(StatesGroup):
    start = State()
     
class PayoutHref(StatesGroup):
    start = State()
    
class PayoutAccount(StatesGroup):
    start = State()
    

class PayoutСonfirm(StatesGroup):
    start = State()
    
class PayoutAccepted(StatesGroup):
    start = State()



# @dp.callback_query_handler(text_contains="balance")
async def getBalance(message: types.message):
    await bot.send_message(message.from_user.id,
        "Выберети баланс",
        reply_markup = get_balance_markup
    )

async def returneChipsBalance(message: types.message):
    userId = message.from_user.id
    with connection.cursor() as cursor:
        find_user = f"SELECT chips FROM users WHERE tele_id = {userId};"
        cursor.execute(find_user)
        chips = cursor.fetchone()
        last_order_request = f"SELECT * FROM payments WHERE id=LAST_INSERT_ID();"
        cursor.execute(last_order_request)
        last_order = cursor.fetchone()
        # order = last_order['order_id']
        
    order = 1
        
    
    
    hash_obj5000RUB = hashlib.md5(bytes(f'6630:15:!s3!yk-OpK!c7Ga:RUB:{order+1}', encoding = 'utf-8'))
    url5000RUB = f"https://pay.freekassa.ru/?m=6630&oa=15&o={order+1}&s={hash_obj5000RUB.hexdigest()}&currency=RUB&us_name=11"
    
    hash_obj5000KZT = hashlib.md5(bytes(f'6630:600:!s3!yk-OpK!c7Ga:KZT:{order+1}', encoding = 'utf-8'))
    url5000KZT = f"https://pay.freekassa.ru/?m=6630&oa=600&o={order+1}&s={hash_obj5000KZT.hexdigest()}&currency=KZT&us_name=11"
    
    
    with connection.cursor() as cursor:
        payment_request5000 = f"INSERT INTO payment (tele_id, chips, value, order_id) VALUES ({userId}, 1, 5000, {order+1}) "
        cursor.execute(payment_request5000)
        connection.commit()
        
    
    
    hash_obj11000RUB = hashlib.md5(bytes(f'6630:200:!s3!yk-OpK!c7Ga:RUB:{order+2}', encoding = 'utf-8'))
    url11000RUB = f"https://pay.freekassa.ru/?m=6630&oa=200&o={order+2}&s={hash_obj11000RUB.hexdigest()}&currency=RUB&us_name=11"
    
    hash_obj11000KZT = hashlib.md5(bytes(f'6630:1200:!s3!yk-OpK!c7Ga:KZT:{order+2}', encoding = 'utf-8'))
    url11000KZT = f"https://pay.freekassa.ru/?m=6630&oa=1200&o={order+2}&s={hash_obj11000KZT.hexdigest()}&currency=KZT&us_name=11"
    
    
    with connection.cursor() as cursor:
        payment_request11000 = f"INSERT INTO payment (tele_id, chips, value, order_id) VALUES ({userId}, 1, 11000, {order+2}) "
        cursor.execute(payment_request11000)
        connection.commit()
    
    
    hash_obj20000RUB = hashlib.md5(bytes(f'6630:300:!s3!yk-OpK!c7Ga:RUB:{order+3}', encoding = 'utf-8'))
    url20000RUB = f"https://pay.freekassa.ru/?m=6630&oa=300&o={order+3}&s={hash_obj20000RUB.hexdigest()}&currency=RUB&us_name=11"
    
    hash_obj20000KZT = hashlib.md5(bytes(f'6630:1800:!s3!yk-OpK!c7Ga:KZT:{order+3}', encoding = 'utf-8'))
    url20000KZT = f"https://pay.freekassa.ru/?m=6630&oa=1800&o={order+3}&s={hash_obj20000KZT.hexdigest()}&currency=KZT&us_name=11"
    
    
    with connection.cursor() as cursor:
        payment_request20000 = f"INSERT INTO payment (tele_id, chips, value, order_id) VALUES ({userId}, 1, 20000, {order+3}) "
        cursor.execute(payment_request20000)
        connection.commit()
    
    
    
    hash_obj30000RUB = hashlib.md5(bytes(f'6630:400:!s3!yk-OpK!c7Ga:RUB:{order+4}', encoding = 'utf-8'))
    url30000RUB = f"https://pay.freekassa.ru/?m=6630&oa=400&o={order+4}&s={hash_obj30000RUB.hexdigest()}&currency=RUB&us_name=11"
    
    hash_obj30000KZT = hashlib.md5(bytes(f'6630:2400:!s3!yk-OpK!c7Ga:KZT:{order+4}', encoding = 'utf-8'))
    url30000KZT = f"https://pay.freekassa.ru/?m=6630&oa=2400&o={order+4}&s={hash_obj30000KZT.hexdigest()}&currency=KZT&us_name=11"
    
    
    
    with connection.cursor() as cursor:
        payment_request30000 = f"INSERT INTO payment (tele_id, chips, value, order_id) VALUES ({userId}, 1, 30000, {order+4}) "
        cursor.execute(payment_request30000)
        connection.commit()
    
    
    hash_obj42000RUB = hashlib.md5(bytes(f'6630:500:!s3!yk-OpK!c7Ga:RUB:{order+5}', encoding = 'utf-8'))
    url42000RUB = f"https://pay.freekassa.ru/?m=6630&oa=500&o={order+5}&s={hash_obj42000RUB.hexdigest()}&currency=RUB&us_name=11"
    
    hash_obj42000KZT = hashlib.md5(bytes(f'6630:3000:!s3!yk-OpK!c7Ga:KZT:{order+5}', encoding = 'utf-8'))
    url42000KZT = f"https://pay.freekassa.ru/?m=6630&oa=3000&o={order+5}&s={hash_obj42000KZT.hexdigest()}&currency=KZT&us_name=11"
    
    
    with connection.cursor() as cursor:
        payment_request42000 = f"INSERT INTO payment (tele_id, chips, value, order_id) VALUES ({userId}, 1, 42000, {order+5}) "
        cursor.execute(payment_request42000)
        connection.commit()
    
    
    
    markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            text = "600тг = 5000 фишек", 
            url=url5000KZT
        ),
        InlineKeyboardButton(
            text = "100₽ = 5000 фишек", 
            url=url5000RUB
        ),
    ).add(
        InlineKeyboardButton(
            text = "1200тг = 11000 фишек", 
            url=url11000KZT
        ),
        InlineKeyboardButton(
            text = "200₽ = 11000 фишек", 
            url=url11000RUB
        ),
    ).add(
        InlineKeyboardButton(
            text = "1800тг = 20000 фишек", 
            url=url20000KZT
        ),
        InlineKeyboardButton(
            text = "300₽ = 20000 фишек", 
            url=url20000RUB
        ),
    ).add(
        InlineKeyboardButton(
            text = "2400тг = 30000 фишек", 
            url=url30000KZT
        ),
        InlineKeyboardButton(
            text = "400₽ = 30000 фишек", 
            url=url30000RUB
        ),
    ).add(
        InlineKeyboardButton(
            text = "2400тг = 42000 фишек", 
            url=url42000KZT
        ),
        InlineKeyboardButton(
            text = "500₽ = 42000 фишек", 
            url=url42000RUB
        ),
    )
    print(markup)
    await bot.send_message(message.from_user.id,
        f"Ваш баланс фишек равен:\
            \n{chips['chips']}", 
        reply_markup = markup
    )



# @dp.callback_query_handler(text_contains="bChips")
async def returneCashBalance(message: types.message):
    userId = message.from_user.id

    with connection.cursor() as cursor:
        find_user = f"SELECT cash FROM users WHERE tele_id = {userId};"
        cursor.execute(find_user)
        cash = cursor.fetchone()
        
    await bot.send_message(message.from_user.id,
        f"Ваш денежный баланс равен:\
            \n{cash['cash']} р. ", 
        reply_markup = returne_balance_cash_markup
    )



# @dp.callback_query_handler(text_contains="buyChips")
async def buyChips(call: types.CallbackQuery):
    await bot.edit_message_text(chat_id=call.message.chat.id, 
        message_id=call.message.message_id,
        text=f"Купить фишки с помощью:", 
        reply_markup = buy_chips_markup
    )


async def transferMoney(message: types.message):
    await bot.send_message(message.from_user.id,
        f"Выберете валюту с для пополнения", 
        reply_markup = currency_markup
    )
    await ReplenishmentCashCurrency.start.set()
    
@dp.message_handler(state = ReplenishmentCashCurrency.start)
async def replenishment_cash_currency(message: types.Message, state: FSMContext):
    await ReplenishmentCashCurrency.next()
    if message.text != "Вернуться назад":
        async with state.proxy() as data:
            data['currency'] = message.text
        await ReplenishmentCashValue.start.set()
        await bot.send_message(message.from_user.id,
            f"Введите ссуму пополнения", 
            reply_markup = back_main_menu_markup 
        )
    
    if message.text == "Вернуться назад":
        await bot.send_message(message.from_user.id,
        f"Привет {message.from_user.first_name}",
        reply_markup = mein_menu_markup
    )
    print(122222222222)
    
    

@dp.message_handler(state = ReplenishmentCashValue.start)
async def replenishment_cash_value(message: types.Message, state: FSMContext):
    await ReplenishmentCashValue.next()
    async with state.proxy() as data:
        currency = data['currency']
    order = 1
    hash_obj = hashlib.md5(bytes(f'6630:{message.text}:!s3!yk-OpK!c7Ga:{currency}:{order+1}', encoding = 'utf-8'))
    url = f"https://pay.freekassa.ru/?m=6630&oa={message.text}&o={order+1}&s={hash_obj.hexdigest()}&currency={currency}"
    if message.text != "Вернуться назад":
        print(55555555555555555555555)
        await bot.send_message(message.from_user.id,
            f"Для оплаты перейдите по ссылке: \n{url}", 
            reply_markup = mein_menu_markup 
        )
        
    if message.text == "Вернуться назад":
        await bot.send_message(message.from_user.id,
        f"Привет {message.from_user.first_name}",
        reply_markup = mein_menu_markup
    )
   
 
 




    
    
async def payoutСurrency(message: types.message, state):
    await bot.send_message(message.from_user.id,
        f"Выбирите валюту для вывода средств", 
        reply_markup = currency_markup
    )   
    await PayoutSistem.start.set()
    
    
@dp.message_handler(state = PayoutSistem.start)
async def payoutSistem(message: types.message, state):
    await PayoutSistem.next()
    if message.text != "Вернуться назад":
        print('!=')
        async with state.proxy() as data:
            data['currency'] = message.text
        
        await bot.send_message(message.from_user.id,
            "Выбирите систему для вывода средств", 
            reply_markup = payout_markup
        )
        await PayoutValue.start.set()
           
    if message.text == "Вернуться назад":
        print('==')
        await bot.send_message(message.from_user.id,
        f"Привет {message.from_user.first_name}",
        reply_markup = mein_menu_markup
    )


@dp.message_handler(state = PayoutValue.start)
async def payoutValue(message: types.message, state):
    await PayoutValue.next()
    if message.text != "Вернуться назад":
        print('!=')
        async with state.proxy() as data:
            data['sistem'] = message.text
            await PayoutAccount.start.set()
        
        await bot.send_message(message.from_user.id,
            f"Введите суму для вывода (больше 100рублей)", 
            reply_markup = back_main_menu_markup
        )
    if message.text == "Вернуться назад":
        print('==')
        await bot.send_message(message.from_user.id,
        f"Привет {message.from_user.first_name}",
        reply_markup = mein_menu_markup
    )
        


@dp.message_handler(state = PayoutAccount.start)
async def payoutAccount(message: types.message, state):
    await PayoutAccount.next()
    if message.text != "Вернуться назад":
        print('!=')
        async with state.proxy() as data:
            data['value'] = message.text
        await PayoutСonfirm.start.set()  
        await bot.send_message(message.from_user.id,
            f"Введите реквезиты для вывода средств\
            \nпример: 5500000000000004", 
            reply_markup = back_main_menu_markup
        )
    if message.text == "Вернуться назад":
        print('==')
        await bot.send_message(message.from_user.id,
        f"Привет {message.from_user.first_name}",
        reply_markup = mein_menu_markup
    )
    
    
@dp.message_handler(state = PayoutСonfirm.start)
async def payoutСonfirm(message: types.message, state):
    await PayoutСonfirm.next()
    if message.text != "Вернуться назад":
        print('!=')
        async with state.proxy() as data:
            data['account'] = message.text
            currency = data['currency']
            sistem = data['sistem']
            value = data['value']
        await PayoutAccepted.start.set()   
        correctly = True
        if correctly == True:
            await bot.send_message(message.from_user.id,
            f"Данные введины правильно?\
            \nВалюта: {currency}\
            \nСистема: {sistem}\
            \nСумма: {value}\
            \nСчет: {message.text}", 
            reply_markup = correctly_markup
        )
    if message.text == "Вернуться назад":
        print('==')
        await bot.send_message(message.from_user.id,
        f"Привет {message.from_user.first_name}",
        reply_markup = mein_menu_markup
    )
    

@dp.message_handler(state = PayoutAccepted.start)
async def payoutHref(message: types.message, state):
    await PayoutAccepted.next()
    # async with state.proxy() as data:
    #     sistem = data['sistem']
    #     currency = data['currency']
    #     value = data['value']
    # account = message.text
    # with connection.cursor() as cursor:
    #     last_order_request = f"SELECT * FROM payments WHERE id=LAST_INSERT_ID();"
    #     cursor.execute(last_order_request)
    #     last_order = cursor.fetchone()
    #     nonce = last_order['order_id']+1
    # signature = "sdf"
    
    # response = requests.post('https://api.freekassa.ru/v1/withdrawals/create', data={
    #     'shopId': 6630, 
    #     "nonce": nonce, 
    #     "signature": signature, 
    #     "i": sistem, 
    #     "account": account, 
    #     "amount": value,
    #     "currency": currency
    #     }
    # )
    # await bot.send_message(message.from_user.id,
    #     f"Средства переведины", 
    #     reply_markup = payout_markup
    # )
    
    # await bot.send_message(message.from_user.id,
    #     f"Возникла ошибка", 
    #     reply_markup = payout_markup
    # )
    
    await bot.send_message(message.from_user.id,
        f"Привет {message.from_user.first_name}",
        reply_markup = mein_menu_markup)


def balance_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(getBalance, text_contains="getBalance" )
    dp.register_message_handler(getBalance, lambda msg: msg.text == "Баланс!" )
    dp.register_message_handler(returneChipsBalance, lambda msg: msg.text == "Баланс фишек" )
    dp.register_message_handler(returneCashBalance, lambda msg: msg.text == "Денежный баланс" )
    dp.register_message_handler(buyChips, lambda msg: msg.text == "Купить Фишки" )
    dp.register_message_handler(transferMoney, lambda msg: msg.text == "Пополнить денежный счет" )
    dp.register_message_handler(payoutСurrency, lambda msg: msg.text == "Вывести деньги со счета" )