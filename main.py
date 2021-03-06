import asyncio
from aiogram.types.reply_keyboard import ReplyKeyboardMarkup
import random
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram import types, executor
from aiogram.dispatcher.storage import FSMContext
from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from attr import asdict
from create_bot import dp, bot, connection, games, loop, publickGames
from handlers import menu, balance, create_game, game, gameP
from keyboards.menu import mein_menu_markup


@dp.message_handler(commands=['k'])
async def start(message: types.Message):
     await bot.send_message(message.from_user.id,
            message
        )




@dp.message_handler(commands=['start'])
async def start(message: types.Message, state):
    userId = message.from_user.id
    with connection.cursor() as cursor:
        find_user = f"SELECT * FROM users WHERE tele_id = {userId};"
        cursor.execute(find_user)
        candidate = cursor.fetchone()
        

        if str(candidate) == 'None':
            add_user = f"INSERT INTO users (tele_id, tele_name, cash, chips, in_game, wins_all_time) VALUES ({userId}, '{message.from_user.username}', 0, 1000, {False}, 0)"
            cursor.execute(add_user)
            connection.commit()
            find_user = f"SELECT * FROM users WHERE tele_id = {userId};"
            cursor.execute(find_user)
            candidate = cursor.fetchone()

    if candidate['in_game'] != 1:
        if " " in message.text:
            info = message.text.split()[1]
            if info.split('-')[0] == 'enter_game':
                hostId = int(info.split('-')[1])
                value_plaears = int(info.split('-')[2])
                playersTeleId = []
                async with state.proxy() as data:
                    data['hostId'] = hostId
                    data['value_plaears'] = value_plaears
                    data['type'] = 0
                players = games[hostId]['players']
                for player in players:
                    playersTeleId.append(player['tele_id'])

                if(len(players) < value_plaears and userId not in playersTeleId):
                    await bot.send_message(message.from_user.id,
                        "???????????????????????????? ?? ????????", 
                        reply_markup=InlineKeyboardMarkup().add(
                            InlineKeyboardButton(
                                text = "????",
                                callback_data = f"join"
                            ),
                            InlineKeyboardButton(
                                text = "??????", 
                                callback_data = f"not_join"
                            )
                        ) 
                    )
                
                if(len(players) >= value_plaears):
                    await bot.send_message(message.from_user.id,
                        "?????????????? ?????? ??????????????????"
                        ) 


                if(userId in playersTeleId):
                    await bot.send_message(message.from_user.id,
                        "???? ?????? ???????????????????? ?? ??????????????"
                        ) 
            if info.split('-')[0] == 'enter_publick_game':
                hostId = int(info.split('-')[1])
                value_plaears = int(info.split('-')[2])
                playersTeleId = []
                async with state.proxy() as data:
                    data['hostId'] = hostId
                    data['value_plaears'] = value_plaears
                    data['type'] = 1
                players = publickGames[hostId]['players']
                table = publickGames[hostId]
                for player in players:
                    playersTeleId.append(player['tele_id'])

                if(len(players) < value_plaears and userId not in playersTeleId):
                    table["wontin"].append({
                        'tele_id': userId,
                        'chat_id': '',
                        'message_id': '',
                        'userNmae': '',
                        'cards': [],
                        'thrownCard': '',
                        'bribe': 0,
                        'bet': 0,
                        'inGame':False,
                        'inAzi': False,
                        'azi': 0,
                        'can_join': False,
                    })
                    
                    with connection.cursor() as cursor:
                        requestDB = f"UPDATE users SET in_game = 1, table_id = '1-{hostId}' WHERE tele_id = {userId};"
                        cursor.execute(requestDB)
                        connection.commit() 
                    await bot.send_message(message.from_user.id,
                        "???????????????????????????? ?? ????????", 
                        reply_markup=InlineKeyboardMarkup().add(
                            InlineKeyboardButton(
                                text = "????",
                                callback_data = f"join"
                            ),
                            InlineKeyboardButton(
                                text = "??????", 
                                callback_data = f"not_join"
                            )
                        ) 
                    ) 
                        
                    
                
                if(len(players) >= value_plaears):
                    await bot.send_message(message.from_user.id,
                        "?????????????? ?????? ??????????????????"
                        ) 


                if(userId in playersTeleId):
                    await bot.send_message(message.from_user.id,
                        "???? ?????? ???????????????????? ?? ??????????????"
                        )     
                
            
            
            if info.split('-')[0] == 'add_friend':
                friend_id = int(info.split('-')[1])
                friend_name = info.split('-')[2]
                
                if friend_id != message.from_user.id:
                
                    can_add = True
                    
                    with connection.cursor() as cursor:
                        find_user = f"SELECT * FROM friends WHERE first_friend = {friend_id};"
                        cursor.execute(find_user)
                        friends = cursor.fetchall()
                        print(candidate)
                        for friend in friends:
                            if friend['second_friend'] == message.from_user.id:
                                can_add = False
                                break
                                
                            
                    if can_add == True:
                        await bot.send_message(message.from_user.id,
                            f"???? ?????????????????? ???????????? ???????????? ???????????? {friend_name}" 
                        )
                        
                        await bot.send_message(int(friend_id),
                            "?????? ???????????????? ???????????? ???????????? " + message.from_user.username, 
                            reply_markup=InlineKeyboardMarkup().add(
                                InlineKeyboardButton(
                                    text = "??????????????",
                                    callback_data = f"append_friend|{message.from_user.id}"
                                ),
                                InlineKeyboardButton(
                                    text = "??????????????????", 
                                    callback_data = f"disdain_friend|{message.from_user.id}"
                                )
                            )        
                        )
                    if can_add == False:
                        await bot.send_message(message.from_user.id,
                            f"?????????? {friend_name} ?????? ?????? ????????" 
                        )
                        
                if friend_id == message.from_user.id:
                    await bot.send_message(message.from_user.id,
                        f"???????????? ???????????????? ???????????? ???????? ?? ????????????" 
                    )
                
        else:
            await bot.send_message(message.from_user.id,
                f"???????????? {message.from_user.first_name}",
                reply_markup = mein_menu_markup
            )
    if candidate['in_game'] == 1:
        await bot.send_message(message.from_user.id,
                f"???? ???????????????????? ?? ????????, ???????? ????????????????????",
                reply_markup = mein_menu_markup
            )
 
 
 

        
 
 
 
@dp.callback_query_handler(text_contains="disdain_friend")    
async def disdain_friend(call: types.callback_query):
    friend_id = int(call.data.split('|')[1])
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    await bot.send_message(friend_id,
            f"?????? ???????????? ???????????? ??????????????????",
        )
    await bot.send_message(call.from_user.id,
            f"???? ?????????????????? ???????????? ????????????"
        )
 
 
 
 
@dp.callback_query_handler(text_contains="append_friend")    
async def append_friend(call: types.callback_query):
    friend_id = int(call.data.split('|')[1])
    with connection.cursor() as cursor:
        add_user_first = f"INSERT INTO friends (first_friend, second_friend) VALUES ({friend_id}, {call.from_user.id})"
        cursor.execute(add_user_first)
        connection.commit()
        add_user_second = f"INSERT INTO friends (first_friend, second_friend) VALUES ({call.from_user.id}, {friend_id})"
        cursor.execute(add_user_second)
        connection.commit()
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    await bot.send_message(friend_id,
        f"?????? ???????????? ???????????? ??????????????"
    )
    await bot.send_message(call.from_user.id,
        f"???? ?????????????? ???????????? ????????????"
    )

     
     
     

@dp.callback_query_handler(text_contains="join")
async def join(call: types.callback_query, state):
    userId = call.from_user.id
    async with state.proxy() as data:
        hostId = data['hostId'] 
        value_plaears = data['value_plaears']
    players = games[hostId]['players'] + games[hostId]['wontin']
    playersTeleId = []
    for player in players:
        playersTeleId.append(player['tele_id'])
        
    print(players)
    
    if(len(players) < value_plaears+1 and userId not in playersTeleId):
        with connection.cursor() as cursor:
            requestDB = f"UPDATE users SET in_game = 1, table_id = '0-{hostId}' WHERE tele_id = {call.from_user.id};"
            cursor.execute(requestDB)
            connection.commit()    
    
        games[hostId]["wontin"].append({
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
            'azi': 0,                                 # ?????? ???????????? ?????? ??????
            'msg': {},                                  # ?????????????????? ?????????????????? 
            'surplus_ceiling': 0,
            "the_move_is_made": True,                   # ?????? ???????????? ?????? ??????
            
        })
        if games[hostId]["gameStarted"] == False:
            players = games[hostId]['players'] + games[hostId]['wontin']
            playersNamws = ""
            for player in players:
                playersNamws = playersNamws +  f"{str(player['userNmae'])} ??????????????????????????\n"

            for player in players:
                if player['tele_id' ] == userId:
                    await bot.edit_message_text(chat_id=call.message.chat.id, 
                        message_id=call.message.message_id,
                        text="???????? ???? ??????????:\n" + playersNamws,
                        reply_markup = InlineKeyboardMarkup().add(
                                InlineKeyboardButton(
                                    text = "?????????? ???? ????????", 
                                    callback_data = f"exit_from_game|0"
                                )
                            ))

                if player['tele_id' ] == hostId:
                    await bot.edit_message_text(chat_id=player['chat_id'], 
                            message_id=player['message_id'],
                            text=f'?????????????????? ?????????????????? ???????? ???????????? ?????? ??????????????????????:\
                                \nhttps://t.me/hwjgnjfdsxjfdibot?start=enter_game-{hostId}\
                                \n\n{playersNamws}', 
                            reply_markup = InlineKeyboardMarkup().add(
                                InlineKeyboardButton(
                                    text = "??????????",
                                    callback_data = f"start_game|"
                                ),
                                InlineKeyboardButton(
                                    text = "???????????????? ????????", 
                                    callback_data = f"cancel_the_game|0"
                                )
                            )
                        )
                if player['tele_id' ] != hostId and player['tele_id' ] != userId:
                    await bot.edit_message_text(chat_id=player['chat_id'], 
                            message_id=player['message_id'],
                            text=f'???????? ???? ??????????:\
                                \n{playersNamws}',
                            reply_markup = InlineKeyboardMarkup().add(
                                InlineKeyboardButton(
                                    text = "?????????? ???? ????????", 
                                    callback_data = f"exit_from_game|0"
                                )
                            )
                        )
        if games[hostId]["gameStarted"] == True:
            await bot.edit_message_text(chat_id=call.message.chat.id, 
                message_id=call.message.message_id,
                text="???? ????????????????????????????, ???????????????? ????????????")
    if(len(players) == value_plaears and userId not in playersTeleId):
        await bot.edit_message_text(chat_id=call.message.chat.id, 
            message_id=call.message.message_id,
            text="?????????????? ??????????????????.")







@dp.callback_query_handler(text_contains="cancel_the_game")
async def cancel_the_game(call: types.callback_query, state):
    type = int(call.data.split('|')[1])
    async with state.proxy() as data:
        hostId = data['hostId']
        
    with connection.cursor() as cursor:
        requestDB = f"UPDATE users SET in_game = 0 WHERE tele_id = {call.from_user.id};"
        cursor.execute(requestDB)
        connection.commit() 
        
        
    if type == 1:
        for player in publickGames[hostId]["players"]:
            await bot.edit_message_text(chat_id=player['chat_id'], 
                    message_id=player['message_id'],
                    text=f'???????? ????????????????'
            )
        publickGames.pop(hostId)
        
    
    if type == 0:
        for player in games[hostId]["players"]:
            await bot.edit_message_text(chat_id=player['chat_id'], 
                    message_id=player['message_id'],
                    text=f'???????? ????????????????'
            )
        del games[hostId]
    print(publickGames)
    
    
@dp.callback_query_handler(text_contains="exit_from_game") 
async def cancel_the_game(call: types.callback_query, state):
    type = int(call.data.split('|')[1])
    async with state.proxy() as data:
        hostId = data['hostId']
    if type == 0:
        table = games[hostId] 
    if type == 1:
        table = publickGames[hostId]
        
    for i, player in enumerate(table["wontin"]):
        if player["tele_id"] == call.from_user.id:
            table["wontin"].pop(i)
            break

    with connection.cursor() as cursor:
        requestDB = f"UPDATE users SET in_game = 0 WHERE tele_id = {call.from_user.id};"
        cursor.execute(requestDB)
        connection.commit()
        
    
    players = table['players'] + table['wontin']
    print(players)
    
    if(len(players) > 1):
        markup = InlineKeyboardMarkup().add(
                        InlineKeyboardButton(
                            text = "??????????",
                            callback_data = f"start_game|"
                        ),
                        InlineKeyboardButton(
                            text = "???????????????? ????????", 
                            callback_data = f"cancel_the_game|{type}"
                        )
                    )
    if(len(players) == 1):
        markup = InlineKeyboardMarkup().add(
            InlineKeyboardButton(
                text = "???????????????? ????????", 
                callback_data = f"cancel_the_game|{type}"
            )
        )
            
    playersNamws = ""
    for player in table["players"]:
        playersNamws = playersNamws +  f"{str(player['userNmae'])} ??????????????????????????\n"
    for player in table["players"]:
        if player['tele_id' ] == hostId:
            await bot.edit_message_text(chat_id=player['chat_id'], 
                    message_id=player['message_id'],
                    text=f'?????????????????? ?????????????????? ???????? ???????????? ?????? ??????????????????????:\
                        \nhttps://t.me/hwjgnjfdsxjfdibot?start=enter_game-{hostId}\
                        \n\n{playersNamws}', 
                    reply_markup = markup
                )
        if player['tele_id' ] != hostId and player['tele_id' ] != hostId:
            await bot.edit_message_text(chat_id=player['chat_id'], 
                    message_id=player['message_id'],
                    text=f'???????? ???? ??????????:\
                        \n{playersNamws}',
                    reply_markup = InlineKeyboardMarkup().add(
                        InlineKeyboardButton(
                            text = "?????????? ???? ????????", 
                            callback_data = f"exit_from_game|{type}"
                        )
                    )
                )
    await bot.edit_message_text(chat_id=call.message.chat.id, 
        message_id=call.message.message_id,
        text="???? ?????????? ???? ????????")
            
    
@dp.callback_query_handler(text_contains="abolition")
async def start(call: types.callback_query, state):
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


@dp.callback_query_handler(text_contains="not_join")
async def start(call: types.callback_query, state):
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)



menu.menu_handlers(dp)
balance.balance_handlers(dp)
create_game.create_game_handlers(dp)
game.game_handlers(dp)
gameP.game_handlers(dp)





if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)