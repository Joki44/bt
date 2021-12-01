from aiogram import types, Dispatcher
from aiogram.types import message
from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from create_bot import dp, bot, games, publickGames, connection
from config import regulationsText
from keyboards.create_game import start_game_markup, tables_markup, create_private_table_markup, create_public_table_markup, value_plaears_public_markup, value_plaears_private_markup



# @dp.callback_query_handler(text_contains="start_game")
async def create_game(message: types.Message):
    await bot.send_message(message.from_user.id,
        "Выберети варинант игры", 
        reply_markup = start_game_markup
    )


# @dp.callback_query_handler(text_contains = "chips")
async def tables (call: types.CallbackQuery):
    valuta = call.data.split('|')[1]
    if(valuta == "chips"):
        await bot.edit_message_text(chat_id=call.message.chat.id, 
            message_id=call.message.message_id,
            text="Выберите вариант игры на фишки:", 
            reply_markup = tables_markup
        )
    if(valuta == "cash"):
        await bot.edit_message_text(chat_id=call.message.chat.id, 
            message_id=call.message.message_id,
            text="Выберите вариант игры на деньги:", 
            reply_markup = tables_markup
        )


# @dp.callback_query_handler(text_contains = "create_private_table")
async def create_private_table(call: types.CallbackQuery, state):
    tableId = call.from_user.id
    value_plaears = call.data.split('|')[1]
    async with state.proxy() as data:
        data['hostId'] = tableId
        data['value_plaears'] = value_plaears
        data['type'] = 0
        
    with connection.cursor() as cursor:
        requestDB = f"UPDATE users SET in_game = 1, table_id = '0-{tableId}' WHERE tele_id = {tableId};"
        cursor.execute(requestDB)
        connection.commit() 
        
    games[tableId] = {
        "carts": 0,                         # игрок который делает ход
        "ceiling": 0,                       # потолок(максимальная ставка)
        "save_ceiling": 0,                  # ставка которое сохранения   
        "value_plaears": value_plaears,     # максимальное количесто игроков
        "cards_on_table": [],               # карты на столе
        "trump": '',                        # козырная карта
        "bet": 0,                           # бакн на кону
        "turns": 0,                         # сделанно ходов в игре
        "valuta": '',                       # валюта на которую будут играть
        "partGame": 0,                      # часть игры
        "CARDS_GAME": [],                   # массив с картами
        "biggest_bet": [0, 0],              # самая большая ставака
        "last_bet": 0,                      # последняя ставка
        "completed": False,                 # показывет завершенно ли действие 
        "namePartGame": 0,                  # название части игры
        "gameStarted": False,               # игра началась 
        "AZI": False,
        "players":                          # массив с игроками
            [{
                'tele_id': tableId,                         # телеграм id игрока
                'chat_id': call.message.chat.id,            # chat id
                'message_id': call.message.message_id ,     # id сообщения
                'userNmae': call.from_user.username,        # username игрока
                'cards': [],                                # карты игрока
                'thrownCard': '',                           # выкинутая карта
                'bribe': 0,                                 # выйграннаые взятки
                'bet': 0,                                   # ставка игрока
                'inGame': True,                             # участвует ли игрок в игре
                'inAzi': False,                             # участвует ли игрок в ази
                'azi': 0,                                   # что делать при ази
                'msg': {},                                  # последнее сообщение 
                'surplus_ceiling': 0,
                "the_move_is_made": True,                   # ход сделан или нет
            }],
        "wontin":[]
    }
    
    url = f"https://t.me/ppwweeqqbot?start=enter_game-{tableId}-{value_plaears}"
    await bot.edit_message_text(chat_id=call.message.chat.id,   
            message_id=call.message.message_id,
            text=f'Создалась приватная игра\
                \nссылка для приглашения:\
                \n{url}', 
            reply_markup = create_private_table_markup
        )


async def create_public_table(call: types.CallbackQuery, state):
    tableId = call.from_user.id
    value_plaears = call.data.split('|')[1]
    async with state.proxy() as data:
        data['hostId'] = len(publickGames)
        data['value_plaears'] = value_plaears
        data['type'] = 1
    
    with connection.cursor() as cursor:
        requestsTable_id = str(len(publickGames))
        requestDB = f"UPDATE users SET in_game = 1, table_id = '1-{requestsTable_id}' WHERE tele_id = {tableId};"
        cursor.execute(requestDB)
        connection.commit()    
    
    
    publickGames.append({
        "carts": 0,                         # игрок который делает ход
        "ceiling": 0,                       # потолок(максимальная ставка)
        "save_ceiling": 0,                  # ставка которое сохранения   
        "value_plaears": value_plaears,     # максимальное количесто игроков
        "cards_on_table": [],               # карты на столе
        "trump": '',                        # козырная карта
        "bet": 0,                           # бакн на кону
        "turns": 0,                         # сделанно ходов в игре
        "valuta": '',                       # валюта на которую будут играть
        "partGame": 0,                      # часть игры
        "CARDS_GAME": [],                   # массив с картами
        "biggest_bet": [0, 0],              # самая большая ставака
        "last_bet": 0,                      # последняя ставка
        "gameStarted": False,               # игра началась 
        "AZI": False,
        "players":                          # массив с игроками
            [{
                'tele_id': tableId,                         # телеграм id игрока
                'chat_id': call.message.chat.id,            # chat id
                'message_id': call.message.message_id ,     # id сообщения
                'userNmae': call.from_user.username,        # username игрока
                'cards': [],                                # карты игрока
                'thrownCard': '',                           # выкинутая карта
                'bribe': 0,                                 # выйграннаые взятки
                'bet': 0,                                   # ставка игрока
                'inGame': True,                             # участвует ли игрок в игре
                'inAzi': False,                             # участвует ли игрок в ази
                'azi': 0                                    # что делать при ази
            }],
        "wontin":[]
    })

    print(publickGames)
    await bot.edit_message_text(chat_id=call.message.chat.id, 
        message_id=call.message.message_id,
        text=f'Создалась публичная игра', 
        reply_markup = create_public_table_markup
    )


async def join_public_table(call: types.CallbackQuery):
    markup = InlineKeyboardMarkup()
    for index, game in enumerate(publickGames):
        markup.add(
            InlineKeyboardButton(
                text = "Игроков: " + str(len(game["players"])),
                callback_data = f"room|{index}|" + str(game["value_plaears"])
            )
        )

    markup.add(
        InlineKeyboardButton(
            text = "Отмена", 
            callback_data = f"abolition"
        )
    )

    await bot.edit_message_text(chat_id=call.message.chat.id, 
            message_id=call.message.message_id,
            text=f'Публичные столы', 
            reply_markup = markup
        )

async def join_room(call: types.CallbackQuery, state):
    userId = call.from_user.id
    tableId = int(call.data.split('|')[1])
    value_plaears = int(call.data.split('|')[2])
    table = publickGames[tableId]
    hostId = table['players'][0]['tele_id']
    playersTeleId = []
    async with state.proxy() as data:
        data['hostId'] = tableId
        data['value_plaears'] = value_plaears
        data['type'] = 1
    with connection.cursor() as cursor:
        requestDB = f"UPDATE users SET in_game = 1, table_id = '1-{tableId}' WHERE tele_id = {userId};"
        cursor.execute(requestDB)
        connection.commit() 
    print(publickGames[tableId])
    players = publickGames[tableId]['players'] + publickGames[tableId]['wontin']
    for player in players:
        playersTeleId.append(player['tele_id'])
    if(len(players) < value_plaears and userId not in playersTeleId):
        table["wontin"].append({
            'tele_id': userId,
            'chat_id': call.message.chat.id,
            'message_id': call.message.message_id,
            'userNmae': call.from_user.username,
            'cards': [],
            'thrownCard': '',
            'bribe': 0,
            'bet': 0,
            'inGame':True,
            'inAzi': False,
            'can_join': False,
            'azi': 0,
        })
        if table["gameStarted"] == False:
            players = publickGames[tableId]['players'] + publickGames[tableId]['wontin']
            playersNamws = ""
            for player in players:
                playersNamws = playersNamws +  f"{str(player['userNmae'])} присоединился\n"

            for player in players:
                    if player['tele_id' ] == userId:
                        await bot.edit_message_text(chat_id=call.message.chat.id, 
                            message_id=call.message.message_id,
                            text="Игра на фишки:\n" + playersNamws)

                    if player['tele_id' ] == hostId:
                        await bot.edit_message_text(chat_id=player['chat_id'], 
                                message_id=player['message_id'],
                                text=f'Создалась публичная игра ссылка для приглашения:\
                                    \n\n{playersNamws}', 
                                reply_markup = InlineKeyboardMarkup().add(
                                    InlineKeyboardButton(
                                        text = "Старт",
                                        callback_data = f"start_public_game|{tableId}"
                                    ),
                                    InlineKeyboardButton(
                                        text = "Отменить игру", 
                                        callback_data = f"cancel_the_game|1"
                                    )
                                )
                            )
                    if player['tele_id' ] != hostId and player['tele_id' ] != userId:
                        await bot.edit_message_text(chat_id=player['chat_id'], 
                                message_id=player['message_id'],
                                text=f'Игра на фишки:\
                                    \n{playersNamws}'
                            )
        if table["gameStarted"] == True:
            await bot.edit_message_text(chat_id=call.message.chat.id, 
                message_id=call.message.message_id,
                text="Вы присоединились, ожидайте начала")
                        
                            
    if(len(players) == value_plaears and userId not in playersTeleId):
        await bot.edit_message_text(chat_id=call.message.chat.id, 
            message_id=call.message.message_id,
            text="Комната заполнена.")
    


async def public_table_players_number(call: types.CallbackQuery):
    await bot.edit_message_text(chat_id=call.message.chat.id, 
            message_id=call.message.message_id,
            text='Выберите количество игроков', 
            reply_markup = value_plaears_public_markup
        )
        


async def private_table_players_number(call: types.CallbackQuery):
    await bot.edit_message_text(chat_id=call.message.chat.id, 
            message_id=call.message.message_id,
            text='Выберите количество игроков', 
            reply_markup = value_plaears_private_markup
        )




def create_game_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(create_game, text_contains="create_game" )
    dp.register_callback_query_handler(tables, text_contains="valuta" )
    dp.register_callback_query_handler(create_private_table, text_contains="create_private_table" )
    dp.register_callback_query_handler(public_table_players_number, text_contains="public_table_players_number" )
    dp.register_callback_query_handler(private_table_players_number, text_contains="private_table_players_number" )
    dp.register_callback_query_handler(create_public_table, text_contains="create_public_table" )
    dp.register_callback_query_handler(join_public_table, text_contains="zxc_public_table" )
    dp.register_callback_query_handler(join_room, text_contains="room" )




    
    dp.register_message_handler(create_game, lambda msg: msg.text == "Начать игру!" )