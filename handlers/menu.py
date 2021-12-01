from aiogram import types, Dispatcher
from aiogram.types import message
from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from create_bot import dp, bot, connection, games, publickGames
from config import regulationsText
from keyboards.menu import mein_menu_markup, setings_markup, language_markup, back_main_menu_markup



# @dp.callback_query_handler(text_contains="back_main_menu")
async def back_main_menu(message: types.message):
    await bot.send_message(message.from_user.id,
        f"Привет {message.from_user.first_name}",
        reply_markup = mein_menu_markup
    )
    
# @dp.callback_query_handler(text_contains="setings")
async def setings(message: types.message):
    await bot.send_message(message.from_user.id,
        "Настройки",
        reply_markup = setings_markup
    )


# @dp.callback_query_handler(text_contains="language")
async def language(message: types.message):
    await bot.send_message(message.from_user.id,
        "Язык",
        reply_markup = language_markup
    )



# @dp.callback_query_handler(text_contains="regulations")
async def regulations(message: types.message):
    await bot.send_message(message.from_user.id,
        regulationsText
    )
    
    
# @dp.message_handler(commands=['friends'])
async def friends(message: types.message):
    mes = f'Ваши друзья\n'
    
    with connection.cursor() as cursor:
        find_user = f"SELECT * FROM friends WHERE first_friend = {message.from_user.id};"
        cursor.execute(find_user)
        friends = cursor.fetchall()
            
    if friends == ():
        await bot.send_message(message.from_user.id, "У вас пока нету друзей")
    if friends != ():
        with connection.cursor() as cursor:
            for friend in friends:
                print(friend)
                find_friend = f"SELECT * FROM users WHERE tele_id = {friend['second_friend']};"
                cursor.execute(find_friend)
                f = cursor.fetchone()
                in_game = 'не в игре'
                if f['in_game'] == 1:
                    tableType = int(f['table_id'].split('-')[0])
                    tableId = int(f['table_id'].split('-')[1])
                    if tableType == 0:
                        value_plaears = games[tableId]["value_plaears"]
                        in_game = f"<a href=\"https://t.me/ppwweeqqbot?start=enter_game-{tableId}-{value_plaears}\">в игре</a>"
                    if tableType == 1:
                        value_plaears = publickGames[tableId]["value_plaears"]
                        in_game = f"<a href=\"https://t.me/ppwweeqqbot?start=enter_publick_game-{tableId}-{value_plaears}\">в игре</a>"
                mes = mes + f"{f['tele_name']}🎖{f['wins_all_time']}💵{f['cash']}🔴{f['chips']} — {in_game}\n"
        await bot.send_message(message.from_user.id, mes ,parse_mode="HTML")

async def exitAZI(call: types.CallbackQuery):
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


def menu_handlers(dp: Dispatcher):
    # dp.register_callback_query_handler(back_main_menu, text_contains="back_main_menu" )
    # dp.register_callback_query_handler(setings, text_contains="setings" )
    # dp.register_callback_query_handler(language, text_contains="language" )
    # dp.register_callback_query_handler(regulations, text_contains="regulations" )
    # dp.register_callback_query_handler(exitAZI, text_contains="exitAZI" )



    dp.register_message_handler(back_main_menu, lambda msg: msg.text == "Вернуться назад" )
    dp.register_message_handler(setings, lambda msg: msg.text == "Настройки" )
    dp.register_message_handler(language, lambda msg: msg.text == "Язык" )
    dp.register_message_handler(regulations, lambda msg: msg.text == "Правила" )
    dp.register_message_handler(friends, lambda msg: msg.text == "Друзья" )
    dp.register_message_handler(exitAZI, lambda msg: msg.text == "Выйти" )