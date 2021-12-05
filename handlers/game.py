import asyncio
from os import closerange
from aiogram.types import message
from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types.reply_keyboard import ReplyKeyboardMarkup
from create_bot import dp, bot, games, publickGames, loop, connection
from config import PLAYING_CARDS, PLAYING_CARDS_BTN_VALUE
from aiogram import types, Dispatcher
import random
from check_equalities import check_equalities
from card_seniority import card_seniority
import copy
from keyboards.menu import mein_menu_markup


from permission_card import permission_card



async def start_game(call: types.CallbackQuery):
    tableId = call.from_user.id
    table = games[tableId]
    table["gameStarted"] = True
    table["m"] = 0
    carts = table["players"][table["carts"]]["tele_id"]
    while len(table["wontin"]) != 0:
        table["players"].append(table["wontin"].pop(0))
        print(2111)
        
    
    table["namePartGame"] = 1
    surplus_ceiling = 0



    table["CARDS_GAME"] = PLAYING_CARDS.copy()
    random.shuffle(table["CARDS_GAME"])
    for player in table["players"]:
        player['cards'].append(table["CARDS_GAME"].pop())
        player['cards'].append(table["CARDS_GAME"].pop())
        player['cards'].append(table["CARDS_GAME"].pop())

    table["trump"] = table["CARDS_GAME"].pop()
    trump = PLAYING_CARDS_BTN_VALUE[table["trump"]]
    for player in table["players"]:
        with connection.cursor() as cursor:
            request_tele_id = player["tele_id"]
            find_user = f"SELECT * FROM users WHERE tele_id = {request_tele_id};"
            cursor.execute(find_user)
            candidate = cursor.fetchone()
            balance = candidate["chips"]
    
        if player["tele_id"] == int(carts):
            bet = table["players"][table["carts"]-1]['bet']
            ccc = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
            msg = await bot.send_message(player['tele_id'],
                f"На кону: 0\
                \nКозырь: {trump}\
                \nВаши карты: {ccc}\
                \nВыберите ставку:",
                reply_markup = InlineKeyboardMarkup().add(
                    InlineKeyboardButton(
                        text = "50",
                        callback_data = f"bet|{tableId}|50|0"
                    ),
                    InlineKeyboardButton(
                        text = "100", 
                        callback_data = f"bet|{tableId}|100|0"
                    ),
                )
            )
            player["msg"] = msg
            player["surplus_ceiling"] = surplus_ceiling
            name = player["userNmae"]
            await bot.send_message(player['tele_id'],
                f"Сейчас ваш ход {name}",
                reply_markup = ReplyKeyboardMarkup().add(
                    ccc
                ).row(
                    "Фишек: " + str(balance)
                ).row(
                    trump, "0"
                ).add(
                    "Ваш ход (на него 25 секунд)"
                ).row(
                    "Спасовать", "Выйти из игры"
                )
            )

            table["players"][table["carts"]]["the_move_is_made"] = False
            loop.create_task(timeIsUp(msg, tableId, surplus_ceiling, table["carts"], table["m"]))


        
        if player["tele_id"] != int(carts):
            ccc = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
            await bot.send_message(player['tele_id'],
                f'На кону: 0\
                \nКозырь: {trump}\
                \nВаши карты: {ccc}\
                \nОжидаем ставики другого игрока',
            )

            name = table["players"][table["carts"]]["userNmae"]
            friend_id = table["players"][table["carts"]]["tele_id"] 
            await bot.send_message(player['tele_id'],
                f"Сейчас ходит <a href=\"https://t.me/ppwweeqqbot?start=add_friend-{friend_id}-{name}\">{name}</a>",parse_mode="HTML",
                reply_markup = ReplyKeyboardMarkup().add(
                    ccc
                ).row(
                    "Фишек: " + str(balance)
                ).row(
                    trump, "0"
                ).add(
                    f"Ожидайем конца хода {name}"
                ).row(
                    "Спасовать", "Выйти из игры"
                )
            )
        



async def set_bet(call:types.CallbackQuery):
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    tableId = int(call.data.split('|')[1])
    table = games[tableId]
    table["m"] += 1
    table["players"][table["carts"]]["the_move_is_made"] = True
    players = []
    noActivePlaers = []
    out = ''
    if call.data.split('|')[2] != 'equal':
        old_bet = int(call.data.split('|')[3])
        surplus_bet = int(call.data.split('|')[2]) + old_bet
        suma = surplus_bet - table["players"][table["carts"]]['bet'] # будет использоваться при запросах в бд
        with connection.cursor() as cursor:
            userIdRequest = table["players"][table["carts"]]['tele_id']
            requestDB = f"UPDATE users SET chips = (chips - {suma}) WHERE tele_id = {userIdRequest};"
            cursor.execute(requestDB)
            connection.commit()
        table["ceiling"] += surplus_bet
        table["players"][table["carts"]]['bet'] = surplus_bet
        old_bet = surplus_bet
            
    if call.data.split('|')[2] == 'equal':
        old_bet = int(call.data.split('|')[3])
        suma = old_bet - table["players"][table["carts"]]['bet']  # будет использоваться при запросах в бд
        table["ceiling"] += suma
        with connection.cursor() as cursor:
            userIdRequest = table["players"][table["carts"]]['tele_id']
            requestDB = f"UPDATE users SET chips = (chips - {suma}) WHERE tele_id = {userIdRequest};"
            cursor.execute(requestDB)
            connection.commit()
        table["players"][table["carts"]]['bet'] = old_bet

    for idx, player in enumerate(table["players"]):
        with connection.cursor() as cursor:
            request_tele_id = player["tele_id"]
            find_user = f"SELECT * FROM users WHERE tele_id = {request_tele_id};"
            cursor.execute(find_user)
            candidate = cursor.fetchone()
            balance = candidate["chips"]
        if player["inGame"] == True:
            if balance < old_bet:
                await bot.send_message(player["tele_id"],
                    "У вас слишком мало фишек, вас исключили",
                    reply_markup = mein_menu_markup
                )
                table["players"].pop(idx)
        if balance < 50:
                table["players"].pop(idx)
                
            
         
    if table["biggest_bet"][0] < table["players"][table["carts"]]['bet']:
        table["biggest_bet"][0] = copy.copy(table["players"][table["carts"]]['bet'])
        table["biggest_bet"][1] = copy.copy(table["carts"])

    for player in table["players"]:
        if player['inGame'] == True:
            players.append(player)
        if player['inGame'] == False:
            noActivePlaers.append(player)


    table["carts"] += 1
    if table["carts"] > (len(table["players"])-1):
        table["carts"] = 0
    while table["players"][table["carts"]]['inGame'] == False:
        table["carts"] += 1
        if table["carts"] > (len(table["players"])-1):
            table["carts"] = 0
    carts = table["players"][table["carts"]]["tele_id"]
    equal = check_equalities(players)


    if equal == False:
        ceiling = table["ceiling"]
        
        trump = PLAYING_CARDS_BTN_VALUE[table["trump"]]
        for player in players:
            with connection.cursor() as cursor:
                request_tele_id = player["tele_id"]
                find_user = f"SELECT * FROM users WHERE tele_id = {request_tele_id};"
                cursor.execute(find_user)
                candidate = cursor.fetchone()
                balance = candidate["chips"]
            if player["tele_id"] == int(carts):
                bet = table["players"][table["carts"]-1]['bet']
                msg = await bot.send_message(player['tele_id'],
                    f"На кону: {ceiling}\
                    \nКозырь: {trump}\
                    \nВаши карты: {PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}\
                    \nВыберите ставку:"+out,
                    reply_markup = InlineKeyboardMarkup().add(
                        InlineKeyboardButton(
                            text = "Уровнять",
                            callback_data = f"bet|{tableId}|equal|{old_bet}"
                        ),
                        InlineKeyboardButton(
                            text = "50",
                            callback_data = f"bet|{tableId}|50|{old_bet}"
                        ),
                        InlineKeyboardButton(
                            text = "100", 
                            callback_data = f"bet|{tableId}|100|{old_bet}"
                        )
                    )
                )  
                player["msg"] = msg
                player["old_bet"] = old_bet
                player["surplus_ceiling"] = old_bet
                name = table["players"][table["carts"]]["userNmae"]
                await bot.send_message(player['tele_id'],
                    f"Сейчас ваш ход {name}",
                    reply_markup = ReplyKeyboardMarkup().add(
                        f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                    ).row(
                        "Фишек: " + str(balance)
                    ).row(
                        trump, str(ceiling)
                    ).add(
                        "Ваш ход (на него 25 секунд)"
                    ).row(
                        "Спасовать", "Выйти из игры"
                    )
                )  
                table["players"][table["carts"]]["the_move_is_made"] = False
                loop.create_task(timeIsUp(msg, tableId, old_bet, table["carts"], table["m"]))




            if player["tele_id"] != int(carts):
                ссс = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                await bot.send_message(player['tele_id'],
                    f'На кону: {ceiling}\
                    \nКозырь: {trump}\
                    \nВаши карты: {ссс}\
                    \nОжидаем ставики другого игрока'+out,
                )
                name = table["players"][table["carts"]]["userNmae"]
                friend_id = table["players"][table["carts"]]["tele_id"]
                await bot.send_message(player['tele_id'],
                    f"Сейчас ходит <a href=\"https://t.me/ppwweeqqbot?start=add_friend-{friend_id}-{name}\">{name}</a>",parse_mode="HTML",
                    reply_markup = ReplyKeyboardMarkup().add(
                        f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                    ).row(
                        "Фишек: " + str(balance)
                    ).row(
                        trump, str(ceiling)
                    ).add(
                        f"Ожидайем конца хода {name}"
                    ).row(
                        "Спасовать", "Выйти из игры"
                    )
                )  
                

    if equal == True:
        ceiling = table["ceiling"]
        
        trump = PLAYING_CARDS_BTN_VALUE[table["trump"]]
        table["carts"] = table["biggest_bet"][1]
        carts = table["players"][table["carts"]]["tele_id"]
        table["namePartGame"] = 2
        for player in players:
            with connection.cursor() as cursor:
                request_tele_id = player["tele_id"]
                find_user = f"SELECT * FROM users WHERE tele_id = {request_tele_id};"
                cursor.execute(find_user)
                candidate = cursor.fetchone()
                balance = candidate["chips"]
            if player["tele_id"] == int(carts):
                msg = await bot.send_message(player['tele_id'],
                    f"На кону: {ceiling}\
                    \nКозырь: {trump}\
                    \nВаши карты: {PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}\
                    \nВыберите ставку:"+out,
                    reply_markup = InlineKeyboardMarkup().add(
                        InlineKeyboardButton(
                            text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]}",
                            callback_data = f"card|{tableId}|{player['cards'][0]}"
                        ),
                        InlineKeyboardButton(
                            text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][1]]}",
                            callback_data = f"card|{tableId}|{player['cards'][1]}"
                        ),
                        InlineKeyboardButton(
                            text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}",
                            callback_data = f"card|{tableId}|{player['cards'][2]}"
                        )
                    )
                )
                player["msg"] = msg
                name = table["players"][table["carts"]]["userNmae"]
                await bot.send_message(player['tele_id'],
                    f"Сейчас ваш ход {name}",
                    reply_markup = ReplyKeyboardMarkup().add(
                        f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                    ).row(
                        "Фишек: " + str(balance)
                    ).row(
                        trump, str(ceiling)
                    ).add(
                        "Ваш ход (на него 25 секунд)"
                    ).row(
                        "Спасовать", "Выйти из игры"
                    )
                ) 

                table["players"][table["carts"]]["the_move_is_made"] = False
                loop.create_task(timeIsUp(msg, tableId, 0, table["carts"], table["m"]))

            if player["tele_id"] != int(carts):
                await bot.send_message(player['tele_id'],
                    f"На кону: {ceiling}\
                    \nКозырь: {trump}\
                    \nВаши карты: {PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]}  {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}\
                    \nОжидаем хода другого игрока"+out,
                )
                name = table["players"][table["carts"]]["userNmae"]
                friend_id = table["players"][table["carts"]]["tele_id"]
                await bot.send_message(player['tele_id'],
                    f"Сейчас ходит <a href=\"https://t.me/ppwweeqqbot?start=add_friend-{friend_id}-{name}\">{name}</a>",parse_mode="HTML",
                    reply_markup = ReplyKeyboardMarkup().add(
                        f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                    ).row(
                        "Фишек: " + str(balance)
                    ).row(
                        trump, str(ceiling)
                    ).add(
                        f"Ожидайем конца хода {name}"
                    ).row(
                        "Спасовать", "Выйти из игры"
                    )
                ) 






async def card_game(call:types.CallbackGame):
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    tableId = int(call.data.split('|')[1])
    table = games[tableId]
    table["m"] += 1
    table["players"][table["carts"]]["the_move_is_made"] = True
    out = ''
    message_vin = ''
    ceiling = table["ceiling"]
    table["save_ceiling"] = ceiling
    print(ceiling)
    trump = PLAYING_CARDS_BTN_VALUE[table["trump"]]
    if call.data.split('|')[2] == 'stop':
        player = table["players"][table["carts"]]
        player['azi'] = 1
        player['inGame']=False
        table["turns"] -= 1
        out = f"\nИгрок {player['userNmae']} спасовал"
        await bot.send_message(player['tele_id'],
            f"Ожидаем конца игры",
        )

    if call.data.split('|')[2] != 'stop':
        card = table["players"][table["carts"]]["cards"].pop(table["players"][table["carts"]]["cards"].index(call.data.split('|')[2]))
        table["cards_on_table"].append(card)
        table["players"][table["carts"]]['thrownCard'] = card

    players = []
    noActivePlaers = []
    for player in table["players"]:
        if player['inGame'] == True:
            players.append(player)
        if player['inGame'] == False:
            noActivePlaers.append(player)
            
    
    table["carts"] += 1
    if table["carts"] > (len(table["players"])-1):
        table["carts"] = 0
    while table["players"][table["carts"]]['inGame'] == False:
        table["carts"] += 1
        if table["carts"] > (len(table["players"])-1):
            table["carts"] = 0

    print(table["carts"])
    table["turns"] += 1
    strCardsOnTable = ""
    strLastCard = ""
    if len(players) <= table["turns"]:
        vin = card_seniority(table["trump"], table["cards_on_table"][0], table["cards_on_table"])
        for player in players:
            if player['thrownCard'] == vin:
                player['bribe'] += 1
                table["carts"] = table["players"].index(player)
                table["turns"] = 0
                table["partGame"] += 1
                table["cards_on_table"] = []
                message_vin = f"\nИгрок {player['userNmae']} выиграл взятку"

    if len(table["cards_on_table"]) > 0:
        strCardsOnTable = f"\nКарты на столе:"
        for card in table["cards_on_table"]:
            strCardsOnTable = strCardsOnTable + ' ' + PLAYING_CARDS_BTN_VALUE[card]
        lastCard = PLAYING_CARDS_BTN_VALUE[table["cards_on_table"][-1]]
        strLastCard = f"\nПоследняя карта которую положили {lastCard}"
    carts = table["players"][table["carts"]]["tele_id"]
    if table["partGame"] < 3:
        for player in players:
            with connection.cursor() as cursor:
                request_tele_id = player["tele_id"]
                find_user = f"SELECT * FROM users WHERE tele_id = {request_tele_id};"
                cursor.execute(find_user)
                candidate = cursor.fetchone()
                balance = candidate["chips"]
            print(table["cards_on_table"])
            if len(table["cards_on_table"]) != 0:
                cardss = permission_card(player['cards'], table["trump"], table["cards_on_table"][0])
            if len(table["cards_on_table"]) == 0:
                cardss = player['cards']
            if len(player['cards']) == 3:
                text = f"Ваши карты: {PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}" + strCardsOnTable + strLastCard
                if len(cardss) == 3:
                    markup = InlineKeyboardMarkup().add(
                        InlineKeyboardButton(
                            text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]}",
                            callback_data = f"card|{tableId}|{player['cards'][0]}"
                        ),
                        InlineKeyboardButton(
                            text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][1]]}",
                            callback_data = f"card|{tableId}|{player['cards'][1]}"
                        ),
                        InlineKeyboardButton(
                            text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}",
                            callback_data = f"card|{tableId}|{player['cards'][2]}"
                        )
                    )

                if len(cardss) == 2:
                    markup = InlineKeyboardMarkup().add(
                        InlineKeyboardButton(
                            text = f"{PLAYING_CARDS_BTN_VALUE[cardss[0]]}",
                            callback_data = f"card|{tableId}|{cardss[0]}"
                        ),
                        InlineKeyboardButton(
                            text = f"{PLAYING_CARDS_BTN_VALUE[cardss[1]]}",
                            callback_data = f"card|{tableId}|{cardss[1]}"
                        )
                    )
                    
                if len(cardss) == 1:
                    markup = InlineKeyboardMarkup().add(
                        InlineKeyboardButton(
                            text = f"{PLAYING_CARDS_BTN_VALUE[cardss[0]]}",
                            callback_data = f"card|{tableId}|{cardss[0]}"
                        )
                    )




                rmarkup = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"

            if len(player['cards']) == 2:
                text = f"Ваши карты: {PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]}" + strCardsOnTable + strLastCard
                if len(cardss) == 2:
                    markup = InlineKeyboardMarkup().add(
                        InlineKeyboardButton(
                            text = f"{PLAYING_CARDS_BTN_VALUE[cardss[0]]}",
                            callback_data = f"card|{tableId}|{cardss[0]}"
                        ),
                        InlineKeyboardButton(
                            text = f"{PLAYING_CARDS_BTN_VALUE[cardss[1]]}",
                            callback_data = f"card|{tableId}|{cardss[1]}"
                        )
                    )
                    
                if len(cardss) == 1:
                    markup = InlineKeyboardMarkup().add(
                        InlineKeyboardButton(
                            text = f"{PLAYING_CARDS_BTN_VALUE[cardss[0]]}",
                            callback_data = f"card|{tableId}|{cardss[0]}"
                        )
                    )
                rmarkup = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]}"

            if len(player['cards']) == 1:
                text = f"Ваши карты: {PLAYING_CARDS_BTN_VALUE[player['cards'][0]]}" + strCardsOnTable + strLastCard
                markup = InlineKeyboardMarkup().add(
                    InlineKeyboardButton(
                        text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]}",
                        callback_data = f"card|{tableId}|{player['cards'][0]}"
                    )
                )
                rmarkup = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} "

            if len(player['cards']) != 0:
                if player["tele_id"] == int(carts):
                    msg = await bot.send_message(player['tele_id'],
                        f"На кону: {ceiling}\
                        \nКозырь: {trump}\n"+text+message_vin+out+"\nВыберите карту:",
                        reply_markup = markup
                    )
                    player["msg"] = msg
                    name = table["players"][table["carts"]]["userNmae"]
                    await bot.send_message(player['tele_id'],
                        f"Сейчас ваш ход {name}",
                        reply_markup = ReplyKeyboardMarkup().add(
                            rmarkup
                        ).row(
                            "Фишек: " + str(balance)
                        ).row(
                            trump, str(ceiling)
                        ).add(
                            "Ваш ход (на него 25 секунд)"
                        ).row(
                            "Спасовать", "Выйти из игры"
                        )
                    ) 

                    table["players"][table["carts"]]["the_move_is_made"] = False
                    loop.create_task(timeIsUp(msg, tableId, 0, table["carts"], table["m"]))

                if player["tele_id"] != int(carts):
                    await bot.send_message(player['tele_id'],
                        f"На кону: {ceiling}\
                        \nКозырь: {trump}\n"+text+message_vin+"\nОжидаем хода другого игрока"+out,
                    )
                    name = table["players"][table["carts"]]["userNmae"]
                    friend_id = table["players"][table["carts"]]["tele_id"]
                    await bot.send_message(player['tele_id'],
                        f"Сейчас ходит <a href=\"https://t.me/ppwweeqqbot?start=add_friend-{friend_id}-{name}\">{name}</a>",parse_mode="HTML",
                        reply_markup = ReplyKeyboardMarkup().add(
                            rmarkup
                        ).row(
                            "Фишек: " + str(balance)
                        ).row(
                            trump, str(ceiling)
                        ).add(
                            f"Ожидайем конца хода {name}"
                        ).row(
                            "Спасовать", "Выйти из игры"
                        )
                    ) 

            if len(player['cards']) == 0:
                text = f"Ваши карты закончились"+out
                if player["tele_id"] == int(carts):
                    await bot.send_message(player['tele_id'],
                        f"На кону: {ceiling}\
                        \nКозырь: {trump}\n"+text+message_vin+out,
                    )

                if player["tele_id"] != int(carts):
                    await bot.send_message(player['tele_id'],
                        f"На кону: {ceiling}\
                        \nКозырь: {trump}\n"+strCardsOnTable+strLastCard+message_vin+out+"\nОжидаем хода другого игрока"+out,
                    )   

    if table["partGame"] == 3:
        bigestBribe = 0
        for player in players:
            if bigestBribe < player['bribe']:
                bigestBribe = player['bribe']
                winer = player['tele_id']
                winerName = player['userNmae']
            if player['bribe'] == 0:
                player['inGame'] = False
                player['azi'] = 1
        
        for player in table["players"]:
            if player['inGame'] == False:
                player['inAzi'] = True

        if bigestBribe > 1 :
            
            with connection.cursor() as cursor:
                suma = int(table["ceiling"])/100*95
                requestDB = f"UPDATE users SET chips = (chips + {suma}) WHERE tele_id = {winer};"
                cursor.execute(requestDB)
                connection.commit()
            while len(table["wontin"]) != 0:
                table["players"].append(table["wontin"].pop(0))
            table["partGame"] = 0
            table["ceiling"] = 0
            table["trump"] = ''
            table["AZI"] = False
            table["CARDS_GAME"] = []
            table["biggest_bet"] = [0, 0]
            print(table)
            for player in table["players"]:
                player['inGame'] = True
                player['inAzi'] = False
                player['azi'] = 1
                player['bet'] = 0
                
            carts = table["players"][table["carts"]]["tele_id"]
            while len(table["wontin"]) != 0:
                table["players"].append(table["wontin"].pop(0))
                print(2111)
            
        
            table["namePartGame"] = 2
            surplus_ceiling = 0



            table["CARDS_GAME"] = PLAYING_CARDS.copy()
            
            random.shuffle(table["CARDS_GAME"])
            for player in table["players"]:
                player['cards'].append(table["CARDS_GAME"].pop())
                player['cards'].append(table["CARDS_GAME"].pop())
                player['cards'].append(table["CARDS_GAME"].pop())

            table["trump"] = table["CARDS_GAME"].pop()
            trump = PLAYING_CARDS_BTN_VALUE[table["trump"]]
            for player in table["players"]:
                with connection.cursor() as cursor:
                    request_tele_id = player["tele_id"]
                    find_user = f"SELECT * FROM users WHERE tele_id = {request_tele_id};"
                    cursor.execute(find_user)
                    candidate = cursor.fetchone()
                    balance = candidate["chips"]
            
                if player["tele_id"] == int(carts):
                    bet = table["players"][table["carts"]-1]['bet']
                    ccc = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                    msg = await bot.send_message(player['tele_id'],
                        f"Вы выиграли этот кон \
                        \nВыберите ставку:",
                        reply_markup = InlineKeyboardMarkup().add(
                            InlineKeyboardButton(
                                text = "50",
                                callback_data = f"bet|{tableId}|50|50"
                            ),
                            InlineKeyboardButton(
                                text = "100", 
                                callback_data = f"bet|{tableId}|100|100"
                            ),
                        )
                    )
                    player["msg"] = msg
                    player["surplus_ceiling"] = surplus_ceiling
                    name = player["userNmae"]
                    await bot.send_message(player['tele_id'],
                        f"Сейчас ваш ход {name}",
                        reply_markup = ReplyKeyboardMarkup().add(
                            ccc
                        ).row(
                            "Фишек: " + str(balance)
                        ).row(
                            trump, "0"
                        ).add(
                            "Ваш ход (на него 25 секунд)"
                        ).row(
                            "Спасовать", "Выйти из игры"
                        )
                    )

                    table["players"][table["carts"]]["the_move_is_made"] = False
                    loop.create_task(timeIsUp(msg, tableId, surplus_ceiling, table["carts"], table["m"]))


                
                if player["tele_id"] != int(carts):
                    ccc = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                    await bot.send_message(player['tele_id'],
                        f"Игрок <a href=\"https://t.me/ppwweeqqbot?start=add_friend-{winer}-{winerName}\">{winerName}</a> выиграл кон\nОжидайте его ставики",
                        parse_mode="HTML",
                    )

                    name = table["players"][table["carts"]]["userNmae"]
                    friend_id = table["players"][table["carts"]]["tele_id"] 
                    await bot.send_message(player['tele_id'],
                        f"Сейчас ходит <a href=\"https://t.me/ppwweeqqbot?start=add_friend-{friend_id}-{name}\">{name}</a>",parse_mode="HTML",
                        reply_markup = ReplyKeyboardMarkup().add(
                            ccc
                        ).row(
                            "Фишек: " + str(balance)
                        ).row(
                            trump, "0"
                        ).add(
                            f"Ожидайем конца хода {name}"
                        ).row(
                            "Спасовать", "Выйти из игры"
                        )
                    )

            
        if bigestBribe <= 1 :
            table["AZI"] = True
            players = []
            noActivePlaers = []
            for player in table["players"]:
                if player['inAzi'] == False:
                    players.append(player)
                if player['inAzi'] == True:
                    noActivePlaers.append(player)
                    
            carts = noActivePlaers[0]["tele_id"]
            for player in noActivePlaers:
                if player["tele_id"] == int(carts):
                    if player['azi'] == 1:
                        prise = ceiling/2
                        msg = await bot.send_message(player['tele_id'],
                            f"На кону: {ceiling}\
                            \nВвариться в АЗИ ценой: фишек {prise}",
                            reply_markup = InlineKeyboardMarkup().add(
                                InlineKeyboardButton(
                                    text = f"Да",
                                    callback_data = f"azi|{tableId}|yes|1"
                                ),
                                InlineKeyboardButton(
                                    text = f"Нет",
                                    callback_data = f"azi|{tableId}|not"
                                )
                            )
                        )
                    if player['azi'] == 2:
                        msg = await bot.send_message(player['tele_id'],
                            f"На кону: {ceiling}\
                            \nВвариться в АЗИ ценой: фишек {ceiling}",
                            reply_markup = InlineKeyboardMarkup().add(
                                InlineKeyboardButton(
                                    text = f"Да",
                                    callback_data = f"azi|{tableId}|yes|2"
                                ),
                                InlineKeyboardButton(
                                    text = f"Нет",
                                    callback_data = f"azi|{tableId}|not"
                                )
                            )
                        )

                if player["tele_id"] != int(carts):
                    await bot.send_message(player['tele_id'],
                        f"Ожидаем выбора других игроков",
                    )
            
            for player in table["players"]:
                if player["tele_id"] == int(carts):
                    player["carts_azi"] = True
                    player["azi_msg"] = msg
                    print(msg)
                    print('msg')
                    print(player["azi_msg"])
                    print('player["azi_msg"]')

            for player in players:
                await bot.send_message(player['tele_id'],
                    f"Ожидаем выбора других игроков",
                )



async def azi(call:types.CallbackGame):
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    tableId = int(call.data.split('|')[1])
    table = games[tableId]
    table["m"] += 1
    answer = call.data.split('|')[2]
    players = []
    ceiling = table["ceiling"]
    save_ceiling = table["save_ceiling"]
    
    
    for player in table["players"]:
        if player["tele_id"] == call.from_user.id:
            player["carts_azi"] = False
    
    for player in table["players"]:
        if player['inAzi'] == True:
            players.append(player)


    if answer == 'yes':
        print('yes')
        player = players[0]
        carts = players[0]["tele_id"]
        answer = call.data.split('|')[3]
        if answer == 1:
            prise = save_ceiling/2
            table["ceiling"] +=  prise
            with connection.cursor() as cursor:
                userIdRequest = table["players"][table["carts"]]['tele_id']
                requestDB = f"UPDATE users SET chips = (chips - {prise}) WHERE tele_id = {userIdRequest};"
                cursor.execute(requestDB)
                connection.commit()
        if answer == 2:
            prise = save_ceiling
            table["ceiling"] +=  prise
            with connection.cursor() as cursor:
                userIdRequest = table["players"][table["carts"]]['tele_id']
                requestDB = f"UPDATE users SET chips = (chips - {prise}) WHERE tele_id = {userIdRequest};"
                cursor.execute(requestDB)
                connection.commit()
        for player in table["players"]:
            if player["tele_id"] == carts:
                player['inGame'] = True
                player['inAzi'] = False
        await bot.send_message(player['tele_id'],
            "Ожидайте выбора игроков",
        )  

    if answer == 'not':
        print('not')
        carts = players[0]["tele_id"]
        for player in table["players"]:
            if player["tele_id"] == carts:
                player['inGame'] = False
                player['inAzi'] = False
        await bot.send_message(carts,
            "Ожидайте конца игры",
        )  
            
    players = []
    for player in table["players"]:
        if player['inAzi'] == True:
            players.append(player)

    if len(players) != 0:
        carts = players[0]["tele_id"]
        for player in table["players"]:
            if player["tele_id"] == int(carts):
                player["carts_azi"] = True
        for player in players:
            if player["tele_id"] == int(carts):
                if player['azi'] == 1:
                    prise = ceiling/2
                    msg = await bot.send_message(player['tele_id'],
                        f"На кону: {ceiling}\
                        \nВвариться в АЗИ ценой: фишек {prise}",
                        reply_markup = InlineKeyboardMarkup().add(
                            InlineKeyboardButton(
                                text = f"Да",
                                callback_data = f"azi|{tableId}|yes|1"
                            ),
                            InlineKeyboardButton(
                                text = f"Нет",
                                callback_data = f"azi|{tableId}|not"
                            )
                        )
                    )
                    player["azi_msg"] = msg
                if player['azi'] == 2:
                    msg = await bot.send_message(player['tele_id'],
                        f"На кону: {ceiling}\
                        \nВвариться в АЗИ ценой: фишек {ceiling}",
                        reply_markup = InlineKeyboardMarkup().add(
                            InlineKeyboardButton(
                                text = f"Да",
                                callback_data = f"azi|{tableId}|yes|2"
                            ),
                            InlineKeyboardButton(
                                text = f"Нет",
                                callback_data = f"azi|{tableId}|not"
                            )
                        )
                    )  
                    player["azi_msg"] = msg

    if len(players) == 0:   
        players = []
        for player in table["players"]:
            if player['inGame'] == True:
                player['inAzi'] == False
                players.append(player)
        table["turns"] = 0
        table["partGame"] = 0
        table["CARDS_GAME"] = PLAYING_CARDS.copy()
        random.shuffle(table["CARDS_GAME"])
        for player in players:
            player['cards'].append(table["CARDS_GAME"].pop())
            player['cards'].append(table["CARDS_GAME"].pop())
            player['cards'].append(table["CARDS_GAME"].pop())
        
        ceiling = table["ceiling"]
        table["trump"] = table["CARDS_GAME"].pop()
        trump = PLAYING_CARDS_BTN_VALUE[table["trump"]]
        carts = table["players"][table["carts"]]['tele_id']
        for player in players:
            with connection.cursor() as cursor:
                request_tele_id = player["tele_id"]
                find_user = f"SELECT * FROM users WHERE tele_id = {request_tele_id};"
                cursor.execute(find_user)
                candidate = cursor.fetchone()
                balance = candidate["chips"]
            if player["tele_id"] == int(carts):
                await bot.send_message(player['tele_id'],
                    f"На кону: {ceiling}\
                    \nКозырь: {trump}\
                    \nВаши карты: {PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}\
                    \nВыберите карту:",
                    reply_markup = InlineKeyboardMarkup().add(
                        InlineKeyboardButton(
                            text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]}",
                            callback_data = f"card|{tableId}|{player['cards'][0]}"
                        ),
                        InlineKeyboardButton(
                            text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][1]]}",
                            callback_data = f"card|{tableId}|{player['cards'][1]}"
                        ),
                        InlineKeyboardButton(
                            text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}",
                            callback_data = f"card|{tableId}|{player['cards'][2]}"
                        )
                    )
                ) 
                ccc = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                name = table["players"][table["carts"]]["userNmae"]
                await bot.send_message(player['tele_id'],
                    f"Сейчас ваш ход {name}",
                    reply_markup = ReplyKeyboardMarkup().add(
                        ccc
                    ).row(
                        "Фишек: " + str(balance)
                    ).row(
                        trump, str(ceiling)
                    ).add(
                        "Ваш ход (на него 25 секунд)"
                    ).row(
                        "Спасовать", "Выйти из игры"
                    )
                )


            if player["tele_id"] != int(carts):
                await bot.send_message(player['tele_id'],
                    f"На кону: {ceiling}\
                    \nКозырь: {trump}\
                    \nВаши карты: {PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}\
                    \nОжидаем хода другого игрока",
                )
                name = table["players"][table["carts"]]['userNmae']
                friend_id = table["players"][table["carts"]]["tele_id"]
                ccc = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                await bot.send_message(player['tele_id'],
                        f"Сейчас ходит <a href=\"https://t.me/ppwweeqqbot?start=add_friend-{friend_id}-{name}\">{name}</a>",parse_mode="HTML",
                    reply_markup = ReplyKeyboardMarkup().add(
                        ccc
                    ).row(
                        "Фишек: " + str(balance)
                    ).row(
                        trump, str(ceiling)
                    ).add(
                        f"Ожидайем конца хода {name}"
                    ).row(
                        "Спасовать", "Выйти из игры"
                    )
                )



# @dp.message_handler(lambda message: message.text == "Спасовать")
async def quitOfTable(message: types.Message, state):
    async with state.proxy() as data:
        tableId = data['hostId']
        type = data['type']
        
    if type == 0:
        table = games[tableId]
    if type == 1:
        table = publickGames[tableId]
    if table["AZI"] == True:
        await bot.send_message(message.from_user.id,
            "Вы не можете спасовать во время АЗИ"
        ) 
    table["m"] += 1
    if table["AZI"] == False:
        for index, player in  enumerate(table["players"]):
            if player["tele_id"] == message.from_user.id:
                indexPl = index
                cartsWin = table["players"][table["carts"]]
                break
        if table["players"][indexPl]['tele_id'] == table["players"][table["carts"]]['tele_id']:
            await bot.delete_message(
                chat_id=table["players"][indexPl]["msg"].chat.id, 
                message_id=table["players"][indexPl]["msg"].message_id
            )
            surplus_ceiling = player["surplus_ceiling"]
            old_bet = surplus_ceiling
            cartsWin = table["players"][table["carts"]]['tele_id']
                
            cartsWin = table["carts"] + 1
            if cartsWin > (len(table["players"])-1):
                cartsWin = 0
            while table["players"][cartsWin]['inGame'] == False:
                cartsWin += 1
                if cartsWin > (len(table["players"])-1):
                    cartsWin = 0
                
            
        players = []
        noActivePlaers = []
        for player in table["players"]:
            if player['inGame'] == True:
                players.append(player)
            if player['inGame'] == False:
                if player['inAzi'] == True:
                    players.append(player)
                if player['inAzi'] == False:
                    noActivePlaers.append(player)
                    
        if len(players) <= 2:
            for player in table["players"]:
                if player['tele_id'] != message.from_user.id:
                    await bot.send_message(player['tele_id'],
                        "Все спасовали, вы выиграли "
                    ) 
                if player['tele_id'] == message.from_user.id:
                    await bot.send_message(player['tele_id'],
                        "Вы спасовали"
                    ) 
            with connection.cursor() as cursor:
                suma = int(table["ceiling"])/100*95
                winer = players[cartsWin]['tele_id']
                requestDB = f"UPDATE users SET chips = (chips + {suma}) WHERE tele_id = {winer};"
                cursor.execute(requestDB)
                connection.commit()
            table["partGame"] = 0
            table["ceiling"] = 0
            table["trump"] = ''
            table["carts"] = cartsWin
            table["CARDS_GAME"] = []
            table["biggest_bet"] = [0, 0]
            print(table)
            for player in table["players"]:
                player['inGame'] = True
                player['inAzi'] = False
                player['azi'] = 1
                player['bet'] = 0

            carts = table["players"][table["carts"]]["tele_id"]
            while len(table["wontin"]) != 0:
                table["players"].append(table["wontin"].pop(0))
                print(2111)
                
            
            table["namePartGame"] = 1
            surplus_ceiling = 0



            table["CARDS_GAME"] = PLAYING_CARDS.copy()
            random.shuffle(table["CARDS_GAME"])
            for player in table["players"]:
                player['cards'].append(table["CARDS_GAME"].pop())
                player['cards'].append(table["CARDS_GAME"].pop())
                player['cards'].append(table["CARDS_GAME"].pop())

            table["trump"] = table["CARDS_GAME"].pop()
            trump = PLAYING_CARDS_BTN_VALUE[table["trump"]]
            for player in table["players"]:
                with connection.cursor() as cursor:
                    request_tele_id = player["tele_id"]
                    find_user = f"SELECT * FROM users WHERE tele_id = {request_tele_id};"
                    cursor.execute(find_user)
                    candidate = cursor.fetchone()
                    balance = candidate["chips"]
            
                if player["tele_id"] == int(carts):
                    bet = table["players"][table["carts"]-1]['bet']
                    ccc = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                    msg = await bot.send_message(player['tele_id'],
                        f"На кону: 0\
                        \nКозырь: {trump}\
                        \nВаши карты: {ccc}\
                        \nВыберите ставку:",
                        reply_markup = InlineKeyboardMarkup().add(
                            InlineKeyboardButton(
                                text = "50",
                                callback_data = f"bet|{tableId}|50|50"
                            ),
                            InlineKeyboardButton(
                                text = "100", 
                                callback_data = f"bet|{tableId}|100|100"
                            ),
                        )
                    )
                    player["msg"] = msg
                    player["surplus_ceiling"] = surplus_ceiling
                    name = player["userNmae"]
                    await bot.send_message(player['tele_id'],
                        f"Сейчас ваш ход {name}",
                        reply_markup = ReplyKeyboardMarkup().add(
                            ccc
                        ).row(
                            "Фишек: " + str(balance)
                        ).row(
                            trump, "0"
                        ).add(
                            "Ваш ход (на него 25 секунд)"
                        ).row(
                            "Спасовать", "Выйти из игры"
                        )
                    )

                    table["players"][table["carts"]]["the_move_is_made"] = False
                    loop.create_task(timeIsUp(msg, tableId, surplus_ceiling, table["carts"], table["m"]))


                
                if player["tele_id"] != int(carts):
                    ccc = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                    await bot.send_message(player['tele_id'],
                        f'На кону: 0\
                        \nКозырь: {trump}\
                        \nВаши карты: {ccc}\
                        \nОжидаем ставики другого игрока',
                    )

                    name = table["players"][table["carts"]]["userNmae"]
                    friend_id = table["players"][table["carts"]]["tele_id"] 
                    await bot.send_message(player['tele_id'],
                        f"Сейчас ходит <a href=\"https://t.me/ppwweeqqbot?start=add_friend-{friend_id}-{name}\">{name}</a>",parse_mode="HTML",
                        reply_markup = ReplyKeyboardMarkup().add(
                            ccc
                        ).row(
                            "Фишек: " + str(balance)
                        ).row(
                            trump, "0"
                        ).add(
                            f"Ожидайем конца хода {name}"
                        ).row(
                            "Спасовать", "Выйти из игры"
                        )
                    )
            
        if len(players) > 2:
            table["players"][indexPl]["inGame"] = False
            table["players"][indexPl]["azi"] = 1
            
            await bot.send_message(message.from_user.id,
            "Вы спасовали ожидайте конца игры"
            )
            
            if table["players"][indexPl]['tele_id'] == table["players"][table["carts"]]['tele_id']:
                if table["namePartGame"] == 1:
                    for player in table["players"]:
                        if player["tele_id"] == message.from_user.id:
                            outgoingPlayer = player
                    
                    print(outgoingPlayer['msg'])        
                    print(outgoingPlayer['msg']["chat"]["id"])        
                    print('msg')        
                    # print(outgoingPlayer['msg']["reply_markup"]["inline_keyboard"][0]["callback_data"])        
                    # print(outgoingPlayer['msg']["reply_markup"]["inline_keyboard"][0])        
                    print("inline_keyboard")           
                    print(outgoingPlayer['msg']["reply_markup"]["inline_keyboard"])           
                    
                    table["players"][table["carts"]]["the_move_is_made"] = True
                    players = []
                    noActivePlaers = []
                    out = ''
                    old_bet = outgoingPlayer["old_bet"] 
                        
                    if table["biggest_bet"][0] < table["players"][table["carts"]]['bet']:
                        table["biggest_bet"][0] = copy.copy(table["players"][table["carts"]]['bet'])
                        table["biggest_bet"][1] = copy.copy(table["carts"])

                    for player in table["players"]:
                        if player['inGame'] == True:
                            players.append(player)
                        if player['inGame'] == False:
                            noActivePlaers.append(player)


                    table["carts"] += 1
                    if table["carts"] > (len(table["players"])-1):
                        table["carts"] = 0
                    while table["players"][table["carts"]]['inGame'] == False:
                        table["carts"] += 1
                        if table["carts"] > (len(table["players"])-1):
                            table["carts"] = 0
                    carts = table["players"][table["carts"]]["tele_id"]
                    equal = check_equalities(players)


                    if equal == False:
                        ceiling = table["ceiling"]
                        
                        trump = PLAYING_CARDS_BTN_VALUE[table["trump"]]
                        for player in players:
                            with connection.cursor() as cursor:
                                request_tele_id = player["tele_id"]
                                find_user = f"SELECT * FROM users WHERE tele_id = {request_tele_id};"
                                cursor.execute(find_user)
                                candidate = cursor.fetchone()
                                balance = candidate["chips"]
                            if player["tele_id"] == int(carts):
                                bet = table["players"][table["carts"]-1]['bet']
                                msg = await bot.send_message(player['tele_id'],
                                    f"На кону: {ceiling}\
                                    \nКозырь: {trump}\
                                    \nВаши карты: {PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}\
                                    \nВыберите ставку:"+out,
                                    reply_markup = InlineKeyboardMarkup().add(
                                        InlineKeyboardButton(
                                            text = "Уровнять",
                                            callback_data = f"bet|{tableId}|equal|{old_bet}"
                                        ),
                                        InlineKeyboardButton(
                                            text = "50",
                                            callback_data = f"bet|{tableId}|50|{old_bet}"
                                        ),
                                        InlineKeyboardButton(
                                            text = "100", 
                                            callback_data = f"bet|{tableId}|100|{old_bet}"
                                        )
                                    )
                                )  
                                player["msg"] = msg
                                player["old_bet"] = old_bet
                                player["surplus_ceiling"] = old_bet
                                name = table["players"][table["carts"]]["userNmae"]
                                await bot.send_message(player['tele_id'],
                                    f"Сейчас ваш ход {name}",
                                    reply_markup = ReplyKeyboardMarkup().add(
                                        f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                                    ).row(
                                        "Фишек: " + str(balance)
                                    ).row(
                                        trump, str(ceiling)
                                    ).add(
                                        "Ваш ход (на него 25 секунд)"
                                    ).row(
                                        "Спасовать", "Выйти из игры"
                                    )
                                )  
                                table["players"][table["carts"]]["the_move_is_made"] = False
                                loop.create_task(timeIsUp(msg, tableId, old_bet, table["carts"], table["m"]))




                            if player["tele_id"] != int(carts):
                                ссс = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                                await bot.send_message(player['tele_id'],
                                    f'На кону: {ceiling}\
                                    \nКозырь: {trump}\
                                    \nВаши карты: {ссс}\
                                    \nОжидаем ставики другого игрока'+out,
                                )
                                name = table["players"][table["carts"]]["userNmae"]
                                friend_id = table["players"][table["carts"]]["tele_id"]
                                await bot.send_message(player['tele_id'],
                                    f"Сейчас ходит <a href=\"https://t.me/ppwweeqqbot?start=add_friend-{friend_id}-{name}\">{name}</a>",parse_mode="HTML",
                                    reply_markup = ReplyKeyboardMarkup().add(
                                        f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                                    ).row(
                                        "Фишек: " + str(balance)
                                    ).row(
                                        trump, str(ceiling)
                                    ).add(
                                        f"Ожидайем конца хода {name}"
                                    ).row(
                                        "Спасовать", "Выйти из игры"
                                    )
                                )  
                                

                    if equal == True:
                        ceiling = table["ceiling"]
                        
                        trump = PLAYING_CARDS_BTN_VALUE[table["trump"]]
                        table["carts"] = table["biggest_bet"][1]
                        carts = table["players"][table["carts"]]["tele_id"]
                        table["namePartGame"] = 2
                        for player in players:
                            with connection.cursor() as cursor:
                                request_tele_id = player["tele_id"]
                                find_user = f"SELECT * FROM users WHERE tele_id = {request_tele_id};"
                                cursor.execute(find_user)
                                candidate = cursor.fetchone()
                                balance = candidate["chips"]
                            if player["tele_id"] == int(carts):
                                msg = await bot.send_message(player['tele_id'],
                                    f"На кону: {ceiling}\
                                    \nКозырь: {trump}\
                                    \nВаши карты: {PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}\
                                    \nВыберите ставку:"+out,
                                    reply_markup = InlineKeyboardMarkup().add(
                                        InlineKeyboardButton(
                                            text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]}",
                                            callback_data = f"card|{tableId}|{player['cards'][0]}"
                                        ),
                                        InlineKeyboardButton(
                                            text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][1]]}",
                                            callback_data = f"card|{tableId}|{player['cards'][1]}"
                                        ),
                                        InlineKeyboardButton(
                                            text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}",
                                            callback_data = f"card|{tableId}|{player['cards'][2]}"
                                        )
                                    )
                                )
                                player["msg"] = msg
                                name = table["players"][table["carts"]]["userNmae"]
                                await bot.send_message(player['tele_id'],
                                    f"Сейчас ваш ход {name}",
                                    reply_markup = ReplyKeyboardMarkup().add(
                                        f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                                    ).row(
                                        "Фишек: " + str(balance)
                                    ).row(
                                        trump, str(ceiling)
                                    ).add(
                                        "Ваш ход (на него 25 секунд)"
                                    ).row(
                                        "Спасовать", "Выйти из игры"
                                    )
                                ) 

                                table["players"][table["carts"]]["the_move_is_made"] = False
                                loop.create_task(timeIsUp(msg, tableId, 0, table["carts"], table["m"]))

                            if player["tele_id"] != int(carts):
                                await bot.send_message(player['tele_id'],
                                    f"На кону: {ceiling}\
                                    \nКозырь: {trump}\
                                    \nВаши карты: {PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]}  {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}\
                                    \nОжидаем хода другого игрока"+out,
                                )
                                name = table["players"][table["carts"]]["userNmae"]
                                friend_id = table["players"][table["carts"]]["tele_id"]
                                await bot.send_message(player['tele_id'],
                                    f"Сейчас ходит <a href=\"https://t.me/ppwweeqqbot?start=add_friend-{friend_id}-{name}\">{name}</a>",parse_mode="HTML",
                                    reply_markup = ReplyKeyboardMarkup().add(
                                        f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                                    ).row(
                                        "Фишек: " + str(balance)
                                    ).row(
                                        trump, str(ceiling)
                                    ).add(
                                        f"Ожидайем конца хода {name}"
                                    ).row(
                                        "Спасовать", "Выйти из игры"
                                    )
                                )  

                if table["namePartGame"] == 2:
                    for player in table["players"]:
                        if player["tele_id"] == message.from_user.id:
                            outgoingPlayer = player
                           
                    
                    
                    table = games[tableId]
                    table["players"][table["carts"]]["the_move_is_made"] = True
                    out = ''
                    message_vin = ''
                    ceiling = table["ceiling"]
                    table["save_ceiling"] = ceiling
                    print(ceiling)
                    trump = PLAYING_CARDS_BTN_VALUE[table["trump"]]

                    players = []
                    noActivePlaers = []
                    for player in table["players"]:
                        if player['inGame'] == True:
                            players.append(player)
                        if player['inGame'] == False:
                            noActivePlaers.append(player)
                            
                    
                    table["carts"] += 1
                    if table["carts"] > (len(table["players"])-1):
                        table["carts"] = 0
                    while table["players"][table["carts"]]['inGame'] == False:
                        table["carts"] += 1
                        if table["carts"] > (len(table["players"])-1):
                            table["carts"] = 0

                    print(table["carts"])
                    table["turns"] += 1
                    strCardsOnTable = ""
                    strLastCard = ""
                    if len(players) <= table["turns"]:
                        vin = card_seniority(table["trump"], table["cards_on_table"][0], table["cards_on_table"])
                        for player in players:
                            if player['thrownCard'] == vin:
                                player['bribe'] += 1
                                table["carts"] = table["players"].index(player)
                                table["turns"] = 0
                                table["partGame"] += 1
                                table["cards_on_table"] = []
                                message_vin = f"\nИгрок {player['userNmae']} выиграл взятку"

                    if len(table["cards_on_table"]) > 0:
                        strCardsOnTable = f"\nКарты на столе:"
                        for card in table["cards_on_table"]:
                            strCardsOnTable = strCardsOnTable + ' ' + PLAYING_CARDS_BTN_VALUE[card]
                        lastCard = PLAYING_CARDS_BTN_VALUE[table["cards_on_table"][-1]]
                        strLastCard = f"\nПоследняя карта которую положили {lastCard}"
                    carts = table["players"][table["carts"]]["tele_id"]
                    if table["partGame"] < 3:
                        for player in players:
                            with connection.cursor() as cursor:
                                request_tele_id = player["tele_id"]
                                find_user = f"SELECT * FROM users WHERE tele_id = {request_tele_id};"
                                cursor.execute(find_user)
                                candidate = cursor.fetchone()
                                balance = candidate["chips"]
                            print(table["cards_on_table"])
                            if len(table["cards_on_table"]) != 0:
                                cardss = permission_card(player['cards'], table["trump"], table["cards_on_table"][0])
                            if len(table["cards_on_table"]) == 0:
                                cardss = player['cards']
                            if len(player['cards']) == 3:
                                text = f"Ваши карты: {PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}" + strCardsOnTable + strLastCard
                                if len(cardss) == 3:
                                    markup = InlineKeyboardMarkup().add(
                                        InlineKeyboardButton(
                                            text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]}",
                                            callback_data = f"card|{tableId}|{player['cards'][0]}"
                                        ),
                                        InlineKeyboardButton(
                                            text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][1]]}",
                                            callback_data = f"card|{tableId}|{player['cards'][1]}"
                                        ),
                                        InlineKeyboardButton(
                                            text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}",
                                            callback_data = f"card|{tableId}|{player['cards'][2]}"
                                        )
                                    )

                                if len(cardss) == 2:
                                    markup = InlineKeyboardMarkup().add(
                                        InlineKeyboardButton(
                                            text = f"{PLAYING_CARDS_BTN_VALUE[cardss[0]]}",
                                            callback_data = f"card|{tableId}|{cardss[0]}"
                                        ),
                                        InlineKeyboardButton(
                                            text = f"{PLAYING_CARDS_BTN_VALUE[cardss[1]]}",
                                            callback_data = f"card|{tableId}|{cardss[1]}"
                                        )
                                    )
                                    
                                if len(cardss) == 1:
                                    markup = InlineKeyboardMarkup().add(
                                        InlineKeyboardButton(
                                            text = f"{PLAYING_CARDS_BTN_VALUE[cardss[0]]}",
                                            callback_data = f"card|{tableId}|{cardss[0]}"
                                        )
                                    )




                                rmarkup = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"

                            if len(player['cards']) == 2:
                                text = f"Ваши карты: {PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]}" + strCardsOnTable + strLastCard
                                if len(cardss) == 2:
                                    markup = InlineKeyboardMarkup().add(
                                        InlineKeyboardButton(
                                            text = f"{PLAYING_CARDS_BTN_VALUE[cardss[0]]}",
                                            callback_data = f"card|{tableId}|{cardss[0]}"
                                        ),
                                        InlineKeyboardButton(
                                            text = f"{PLAYING_CARDS_BTN_VALUE[cardss[1]]}",
                                            callback_data = f"card|{tableId}|{cardss[1]}"
                                        )
                                    )
                                    
                                if len(cardss) == 1:
                                    markup = InlineKeyboardMarkup().add(
                                        InlineKeyboardButton(
                                            text = f"{PLAYING_CARDS_BTN_VALUE[cardss[0]]}",
                                            callback_data = f"card|{tableId}|{cardss[0]}"
                                        )
                                    )
                                rmarkup = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]}"

                            if len(player['cards']) == 1:
                                text = f"Ваши карты: {PLAYING_CARDS_BTN_VALUE[player['cards'][0]]}" + strCardsOnTable + strLastCard
                                markup = InlineKeyboardMarkup().add(
                                    InlineKeyboardButton(
                                        text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]}",
                                        callback_data = f"card|{tableId}|{player['cards'][0]}"
                                    )
                                )
                                rmarkup = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} "

                            if len(player['cards']) != 0:
                                if player["tele_id"] == int(carts):
                                    msg = await bot.send_message(player['tele_id'],
                                        f"На кону: {ceiling}\
                                        \nКозырь: {trump}\n"+text+message_vin+out+"\nВыберите карту:",
                                        reply_markup = markup
                                    )
                                    player["msg"] = msg
                                    name = table["players"][table["carts"]]["userNmae"]
                                    await bot.send_message(player['tele_id'],
                                        f"Сейчас ваш ход {name}",
                                        reply_markup = ReplyKeyboardMarkup().add(
                                            rmarkup
                                        ).row(
                                            "Фишек: " + str(balance)
                                        ).row(
                                            trump, str(ceiling)
                                        ).add(
                                            "Ваш ход (на него 25 секунд)"
                                        ).row(
                                            "Спасовать", "Выйти из игры"
                                        )
                                    ) 

                                    table["players"][table["carts"]]["the_move_is_made"] = False
                                    loop.create_task(timeIsUp(msg, tableId, 0, table["carts"], table["m"]))

                                if player["tele_id"] != int(carts):
                                    await bot.send_message(player['tele_id'],
                                        f"На кону: {ceiling}\
                                        \nКозырь: {trump}\n"+text+message_vin+"\nОжидаем хода другого игрока"+out,
                                    )
                                    name = table["players"][table["carts"]]["userNmae"]
                                    friend_id = table["players"][table["carts"]]["tele_id"]
                                    await bot.send_message(player['tele_id'],
                                        f"Сейчас ходит <a href=\"https://t.me/ppwweeqqbot?start=add_friend-{friend_id}-{name}\">{name}</a>",parse_mode="HTML",
                                        reply_markup = ReplyKeyboardMarkup().add(
                                            rmarkup
                                        ).row(
                                            "Фишек: " + str(balance)
                                        ).row(
                                            trump, str(ceiling)
                                        ).add(
                                            f"Ожидайем конца хода {name}"
                                        ).row(
                                            "Спасовать", "Выйти из игры"
                                        )
                                    ) 

                            if len(player['cards']) == 0:
                                text = f"Ваши карты закончились"+out
                                if player["tele_id"] == int(carts):
                                    await bot.send_message(player['tele_id'],
                                        f"На кону: {ceiling}\
                                        \nКозырь: {trump}\n"+text+message_vin+out,
                                    )

                                if player["tele_id"] != int(carts):
                                    await bot.send_message(player['tele_id'],
                                        f"На кону: {ceiling}\
                                        \nКозырь: {trump}\n"+strCardsOnTable+strLastCard+message_vin+out+"\nОжидаем хода другого игрока"+out,
                                    )   

                    if table["partGame"] == 3:
                        bigestBribe = 0
                        for player in players:
                            if bigestBribe < player['bribe']:
                                bigestBribe = player['bribe']
                                winer = player['tele_id']
                                winerName = player['userNmae']
                            if player['bribe'] == 0:
                                player['inGame'] = False
                                player['azi'] = 1
                        
                        for player in table["players"]:
                            if player['inGame'] == False:
                                player['inAzi'] = True

                        if bigestBribe > 1 :
                            with connection.cursor() as cursor:
                                suma = int(table["ceiling"])/100*95
                                requestDB = f"UPDATE users SET chips = (chips + {suma}) WHERE tele_id = {winer};"
                                cursor.execute(requestDB)
                                connection.commit()
                            while len(table["wontin"]) != 0:
                                table["players"].append(table["wontin"].pop(0))
                            table["partGame"] = 0
                            table["ceiling"] = 0
                            table["trump"] = ''
                            table["AZI"] = False
                            table["CARDS_GAME"] = []
                            table["biggest_bet"] = [0, 0]
                            print(table)
                            for player in table["players"]:
                                player['inGame'] = True
                                player['inAzi'] = False
                                player['azi'] = 1
                                player['bet'] = 0
                                
                            carts = table["players"][table["carts"]]["tele_id"]
                            while len(table["wontin"]) != 0:
                                table["players"].append(table["wontin"].pop(0))
                                print(2111)
                            
                        
                            table["namePartGame"] = 2
                            surplus_ceiling = 0



                            table["CARDS_GAME"] = PLAYING_CARDS.copy()
                            
                            random.shuffle(table["CARDS_GAME"])
                            for player in table["players"]:
                                player['cards'].append(table["CARDS_GAME"].pop())
                                player['cards'].append(table["CARDS_GAME"].pop())
                                player['cards'].append(table["CARDS_GAME"].pop())

                            table["trump"] = table["CARDS_GAME"].pop()
                            trump = PLAYING_CARDS_BTN_VALUE[table["trump"]]
                            for player in table["players"]:
                                with connection.cursor() as cursor:
                                    request_tele_id = player["tele_id"]
                                    find_user = f"SELECT * FROM users WHERE tele_id = {request_tele_id};"
                                    cursor.execute(find_user)
                                    candidate = cursor.fetchone()
                                    balance = candidate["chips"]
                            
                                if player["tele_id"] == int(carts):
                                    bet = table["players"][table["carts"]-1]['bet']
                                    ccc = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                                    msg = await bot.send_message(player['tele_id'],
                                        f"Вы выиграли этот кон \
                                        \nВыберите ставку:",
                                        reply_markup = InlineKeyboardMarkup().add(
                                            InlineKeyboardButton(
                                                text = "50",
                                                callback_data = f"bet|{tableId}|50|50"
                                            ),
                                            InlineKeyboardButton(
                                                text = "100", 
                                                callback_data = f"bet|{tableId}|100|100"
                                            ),
                                        )
                                    )
                                    player["msg"] = msg
                                    player["surplus_ceiling"] = surplus_ceiling
                                    name = player["userNmae"]
                                    await bot.send_message(player['tele_id'],
                                        f"Сейчас ваш ход {name}",
                                        reply_markup = ReplyKeyboardMarkup().add(
                                            ccc
                                        ).row(
                                            "Фишек: " + str(balance)
                                        ).row(
                                            trump, "0"
                                        ).add(
                                            "Ваш ход (на него 25 секунд)"
                                        ).row(
                                            "Спасовать", "Выйти из игры"
                                        )
                                    )

                                    table["players"][table["carts"]]["the_move_is_made"] = False
                                    loop.create_task(timeIsUp(msg, tableId, surplus_ceiling, table["carts"], table["m"]))


                                
                                if player["tele_id"] != int(carts):
                                    ccc = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                                    await bot.send_message(player['tele_id'],
                                        f"Игрок <a href=\"https://t.me/ppwweeqqbot?start=add_friend-{winer}-{winerName}\">{winerName}</a> выиграл кон\nОжидайте его ставики",
                                        parse_mode="HTML",
                                    )

                                    name = table["players"][table["carts"]]["userNmae"]
                                    friend_id = table["players"][table["carts"]]["tele_id"] 
                                    await bot.send_message(player['tele_id'],
                                        f"Сейчас ходит <a href=\"https://t.me/ppwweeqqbot?start=add_friend-{friend_id}-{name}\">{name}</a>",parse_mode="HTML",
                                        reply_markup = ReplyKeyboardMarkup().add(
                                            ccc
                                        ).row(
                                            "Фишек: " + str(balance)
                                        ).row(
                                            trump, "0"
                                        ).add(
                                            f"Ожидайем конца хода {name}"
                                        ).row(
                                            "Спасовать", "Выйти из игры"
                                        )
                                    )

                            
                        if bigestBribe <= 1 :
                            table["AZI"] = True
                            players = []
                            noActivePlaers = []
                            for player in table["players"]:
                                if player['inAzi'] == False:
                                    players.append(player)
                                if player['inAzi'] == True:
                                    noActivePlaers.append(player)
                                    
                            carts = noActivePlaers[0]["tele_id"]
                            for player in noActivePlaers:
                                if player["tele_id"] == int(carts):
                                    if player['azi'] == 1:
                                        prise = ceiling/2
                                        msg = await bot.send_message(player['tele_id'],
                                            f"На кону: {ceiling}\
                                            \nВвариться в АЗИ ценой: фишек {prise}",
                                            reply_markup = InlineKeyboardMarkup().add(
                                                InlineKeyboardButton(
                                                    text = f"Да",
                                                    callback_data = f"azi|{tableId}|yes|1"
                                                ),
                                                InlineKeyboardButton(
                                                    text = f"Нет",
                                                    callback_data = f"azi|{tableId}|not"
                                                )
                                            )
                                        )
                                    if player['azi'] == 2:
                                        msg = await bot.send_message(player['tele_id'],
                                            f"На кону: {ceiling}\
                                            \nВвариться в АЗИ ценой: фишек {ceiling}",
                                            reply_markup = InlineKeyboardMarkup().add(
                                                InlineKeyboardButton(
                                                    text = f"Да",
                                                    callback_data = f"azi|{tableId}|yes|2"
                                                ),
                                                InlineKeyboardButton(
                                                    text = f"Нет",
                                                    callback_data = f"azi|{tableId}|not"
                                                )
                                            )
                                        )

                                if player["tele_id"] != int(carts):
                                    await bot.send_message(player['tele_id'],
                                        f"Ожидаем выбора других игроков",
                                    )
                            
                            for player in table["players"]:
                                if player["tele_id"] == int(carts):
                                    player["carts_azi"] = True
                                    player["azi_msg"] = msg
                                    print(msg)
                                    print('msg')
                                    print(player["azi_msg"])
                                    print('player["azi_msg"]')

                            for player in players:
                                await bot.send_message(player['tele_id'],
                                    f"Ожидаем выбора других игроков",
                                )
          
          
          
          
          
                

async def timeIsUp(message, tableId, surplus_ceiling, carts, m):
    table = games[tableId]
    outgoingPlayer = table["players"][carts]
    await asyncio.sleep(25)
    if table["m"] == m:
        if table["players"][carts]["the_move_is_made"] == False:  
            table["m"] += 1
            await bot.send_message(message["chat"]["id"],
                "Вы ничего не сделали и спасовали"
            ) 
            print(table["players"][carts])
            table["players"][carts]["inGame"] = False
            table["players"][carts]["inAzi"] = True
            table["players"][carts]["azi"] = 1
            
            table["players"][carts]["the_move_is_made"] = True 
            # await bot.delete_message(
            #     chat_id=message.chat.id, 
            #     message_id=message.message_id
            # )
            old_bet = surplus_ceiling
            
                
            players = []
            noActivePlaers = []
            for player in table["players"]:
                if player['inGame'] == True:
                    players.append(player)
                if player['inGame'] == False:
                    # if player['inAzi'] == True:
                    #     players.append(player)
                    # if player['inAzi'] == False:
                    noActivePlaers.append(player)
            
            print(players)
                        
            if len(players) < 2:
                table["carts"] += 1
                if table["carts"] > (len(table["players"])-1):
                    table["carts"] = 0
                while table["players"][table["carts"]]['inGame'] == False:
                    table["carts"] += 1
                    if table["carts"] > (len(table["players"])-1):
                        table["carts"] = 0
                
                winerName = table["players"][table["carts"]]["userNmae"]
                for player in table["players"]:
                    if player['tele_id'] == table["players"][table["carts"]]:
                        await bot.send_message(player['tele_id'],
                            "Все спасовали, вы выиграли "
                        ) 
                    if player['tele_id'] != message.from_user.id:
                        await bot.send_message(player['tele_id'],
                            f"Все спасовали, игрок {winerName} выиграл"
                        ) 
                with connection.cursor() as cursor:
                    suma = int(table["ceiling"])/100*95
                    winer = table["players"][table["carts"]]['tele_id']
                    requestDB = f"UPDATE users SET chips = (chips + {suma}) WHERE tele_id = {winer};"
                    cursor.execute(requestDB)
                    connection.commit()
                table["partGame"] = 0
                table["ceiling"] = 0
                table["trump"] = ''
                table["CARDS_GAME"] = []
                table["biggest_bet"] = [0, 0]
                print(table)
                for player in table["players"]:
                    player['inGame'] = True
                    player['inAzi'] = False
                    player['azi'] = 1
                    player['bet'] = 0

                carts = table["players"][table["carts"]]["tele_id"]
                while len(table["wontin"]) != 0:
                    table["players"].append(table["wontin"].pop(0))
                    print(2111)
                    
                
                table["namePartGame"] = 1
                surplus_ceiling = 0



                table["CARDS_GAME"] = PLAYING_CARDS.copy()
                random.shuffle(table["CARDS_GAME"])
                for player in table["players"]:
                    player['cards'].append(table["CARDS_GAME"].pop())
                    player['cards'].append(table["CARDS_GAME"].pop())
                    player['cards'].append(table["CARDS_GAME"].pop())

                table["trump"] = table["CARDS_GAME"].pop()
                trump = PLAYING_CARDS_BTN_VALUE[table["trump"]]
                for player in table["players"]:
                    with connection.cursor() as cursor:
                        request_tele_id = player["tele_id"]
                        find_user = f"SELECT * FROM users WHERE tele_id = {request_tele_id};"
                        cursor.execute(find_user)
                        candidate = cursor.fetchone()
                        balance = candidate["chips"]
                
                    if player["tele_id"] == int(carts):
                        bet = table["players"][table["carts"]-1]['bet']
                        ccc = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                        msg = await bot.send_message(player['tele_id'],
                            f"На кону: 0\
                            \nКозырь: {trump}\
                            \nВаши карты: {ccc}\
                            \nВыберите ставку:",
                            reply_markup = InlineKeyboardMarkup().add(
                                InlineKeyboardButton(
                                    text = "50",
                                    callback_data = f"bet|{tableId}|50|50"
                                ),
                                InlineKeyboardButton(
                                    text = "100", 
                                    callback_data = f"bet|{tableId}|100|100"
                                ),
                            )
                        )
                        player["msg"] = msg
                        player["surplus_ceiling"] = surplus_ceiling
                        name = player["userNmae"]
                        await bot.send_message(player['tele_id'],
                            f"Сейчас ваш ход {name}",
                            reply_markup = ReplyKeyboardMarkup().add(
                                ccc
                            ).row(
                                "Фишек: " + str(balance)
                            ).row(
                                trump, "0"
                            ).add(
                                "Ваш ход (на него 25 секунд)"
                            ).row(
                                "Спасовать", "Выйти из игры"
                            )
                        )

                        table["players"][table["carts"]]["the_move_is_made"] = False
                        loop.create_task(timeIsUp(msg, tableId, surplus_ceiling, table["carts"], table["m"]))


                    
                    if player["tele_id"] != int(carts):
                        ccc = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                        await bot.send_message(player['tele_id'],
                            f'На кону: 0\
                            \nКозырь: {trump}\
                            \nВаши карты: {ccc}\
                            \nОжидаем ставики другого игрока',
                        )

                        name = table["players"][table["carts"]]["userNmae"]
                        friend_id = table["players"][table["carts"]]["tele_id"] 
                        await bot.send_message(player['tele_id'],
                            f"Сейчас ходит <a href=\"https://t.me/ppwweeqqbot?start=add_friend-{friend_id}-{name}\">{name}</a>",parse_mode="HTML",
                            reply_markup = ReplyKeyboardMarkup().add(
                                ccc
                            ).row(
                                "Фишек: " + str(balance)
                            ).row(
                                trump, "0"
                            ).add(
                                f"Ожидайем конца хода {name}"
                            ).row(
                                "Спасовать", "Выйти из игры"
                            )
                        )
                    
            if len(players) >= 2:  
                if table["AZI"] == True:
                    for player in table["players"]:
                        if player["tele_id"] == message.from_user.id:
                            print(player["azi_msg"])
                            print(player["azi_msg"]["message_id"])
                            print(player["azi_msg"]["chat"]["id"])
                            if player["carts_azi"] == True:
                                # await bot.delete_message(chat_id=player["azi_msg"]["chat"]["id"], message_id=player["azi_msg"]["message_id"])
                                players = []
                                ceiling = table["ceiling"]
                                save_ceiling = table["save_ceiling"]
                                
                                
                                for player in table["players"]:
                                    if player['inAzi'] == True:
                                        players.append(player)


                                carts = players[0]["tele_id"]
                                for player in table["players"]:
                                    if player["tele_id"] == carts:
                                        player['inGame'] = False
                                        player['inAzi'] = False
                                        
                                players = []
                                for player in table["players"]:
                                    if player['inAzi'] == True:
                                        players.append(player)

                                if len(players) != 0:
                                    carts = players[0]["tele_id"]
                                    for player in table["players"]:
                                        if player["tele_id"] == int(carts):
                                            player["carts_azi"] = True
                                    for player in players:
                                        if player["tele_id"] == int(carts):
                                            if player['azi'] == 1:
                                                prise = ceiling/2
                                                msg = await bot.send_message(player['tele_id'],
                                                    f"На кону: {ceiling}\
                                                    \nВвариться в АЗИ ценой: фишек {prise}",
                                                    reply_markup = InlineKeyboardMarkup().add(
                                                        InlineKeyboardButton(
                                                            text = f"Да",
                                                            callback_data = f"azi|{tableId}|yes|1"
                                                        ),
                                                        InlineKeyboardButton(
                                                            text = f"Нет",
                                                            callback_data = f"azi|{tableId}|not"
                                                        )
                                                    )
                                                )
                                            if player['azi'] == 2:
                                                msg = await bot.send_message(player['tele_id'],
                                                    f"На кону: {ceiling}\
                                                    \nВвариться в АЗИ ценой: фишек {ceiling}",
                                                    reply_markup = InlineKeyboardMarkup().add(
                                                        InlineKeyboardButton(
                                                            text = f"Да",
                                                            callback_data = f"azi|{tableId}|yes|2"
                                                        ),
                                                        InlineKeyboardButton(
                                                            text = f"Нет",
                                                            callback_data = f"azi|{tableId}|not"
                                                        )
                                                    )
                                                )  
                                            
                                        for player in table["players"]:
                                            if player["tele_id"] == int(carts):
                                                player["carts_azi"] = True
                                                player["azi_msg"] = msg

                                if len(players) == 0:   
                                    players = []
                                    for player in table["players"]:
                                        if player['inGame'] == True:
                                            player['inAzi'] == False
                                            players.append(player)
                                    table["turns"] = 0
                                    table["partGame"] = 0
                                    table["CARDS_GAME"] = PLAYING_CARDS.copy()
                                    random.shuffle(table["CARDS_GAME"])
                                    for player in players:
                                        player['cards'].append(table["CARDS_GAME"].pop())
                                        player['cards'].append(table["CARDS_GAME"].pop())
                                        player['cards'].append(table["CARDS_GAME"].pop())
                                    
                                    ceiling = table["ceiling"]
                                    table["trump"] = table["CARDS_GAME"].pop()
                                    trump = PLAYING_CARDS_BTN_VALUE[table["trump"]]
                                    carts = table["players"][table["carts"]]['tele_id']
                                    for player in players:
                                        with connection.cursor() as cursor:
                                            request_tele_id = player["tele_id"]
                                            find_user = f"SELECT * FROM users WHERE tele_id = {request_tele_id};"
                                            cursor.execute(find_user)
                                            candidate = cursor.fetchone()
                                            balance = candidate["chips"]
                                        if player["tele_id"] == int(carts):
                                            await bot.send_message(player['tele_id'],
                                                f"На кону: {ceiling}\
                                                \nКозырь: {trump}\
                                                \nВаши карты: {PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}\
                                                \nВыберите карту:",
                                                reply_markup = InlineKeyboardMarkup().add(
                                                    InlineKeyboardButton(
                                                        text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]}",
                                                        callback_data = f"card|{tableId}|{player['cards'][0]}"
                                                    ),
                                                    InlineKeyboardButton(
                                                        text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][1]]}",
                                                        callback_data = f"card|{tableId}|{player['cards'][1]}"
                                                    ),
                                                    InlineKeyboardButton(
                                                        text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}",
                                                        callback_data = f"card|{tableId}|{player['cards'][2]}"
                                                    )
                                                )
                                            ) 
                                            ccc = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                                            name = table["players"][table["carts"]]["userNmae"]
                                            await bot.send_message(player['tele_id'],
                                                f"Сейчас ваш ход {name}",
                                                reply_markup = ReplyKeyboardMarkup().add(
                                                    ccc
                                                ).row(
                                                    "Фишек: " + str(balance)
                                                ).row(
                                                    trump, str(ceiling)
                                                ).add(
                                                    "Ваш ход (на него 25 секунд)"
                                                ).row(
                                                    "Спасовать", "Выйти из игры"
                                                )
                                            )


                                        if player["tele_id"] != int(carts):
                                            await bot.send_message(player['tele_id'],
                                                f"На кону: {ceiling}\
                                                \nКозырь: {trump}\
                                                \nВаши карты: {PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}\
                                                \nОжидаем хода другого игрока",
                                            )
                                            name = table["players"][table["carts"]]['userNmae']
                                            friend_id = table["players"][table["carts"]]["tele_id"]
                                            ccc = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                                            await bot.send_message(player['tele_id'],
                                                    f"Сейчас ходит <a href=\"https://t.me/ppwweeqqbot?start=add_friend-{friend_id}-{name}\">{name}</a>",parse_mode="HTML",
                                                reply_markup = ReplyKeyboardMarkup().add(
                                                    ccc
                                                ).row(
                                                    "Фишек: " + str(balance)
                                                ).row(
                                                    trump, str(ceiling)
                                                ).add(
                                                    f"Ожидайем конца хода {name}"
                                                ).row(
                                                    "Спасовать", "Выйти из игры"
                                                )
                                            )
                    
                if table["AZI"] == False:
                    if True:
                        if table["namePartGame"] == 1:
                            table["players"][table["carts"]]["the_move_is_made"] = True
                            players = []
                            noActivePlaers = []
                            out = ''
                                
                            if table["biggest_bet"][0] < table["players"][table["carts"]]['bet']:
                                table["biggest_bet"][0] = copy.copy(table["players"][table["carts"]]['bet'])
                                table["biggest_bet"][1] = copy.copy(table["carts"])

                            for player in table["players"]:
                                if player['inGame'] == True:
                                    players.append(player)
                                if player['inGame'] == False:
                                    noActivePlaers.append(player)


                            table["carts"] += 1
                            if table["carts"] > (len(table["players"])-1):
                                table["carts"] = 0
                            while table["players"][table["carts"]]['inGame'] == False:
                                table["carts"] += 1
                                if table["carts"] > (len(table["players"])-1):
                                    table["carts"] = 0
                            carts = table["players"][table["carts"]]["tele_id"]
                            equal = check_equalities(players)


                            if equal == False:
                                ceiling = table["ceiling"]
                                
                                trump = PLAYING_CARDS_BTN_VALUE[table["trump"]]
                                for player in players:
                                    with connection.cursor() as cursor:
                                        request_tele_id = player["tele_id"]
                                        find_user = f"SELECT * FROM users WHERE tele_id = {request_tele_id};"
                                        cursor.execute(find_user)
                                        candidate = cursor.fetchone()
                                        balance = candidate["chips"]
                                    if player["tele_id"] == int(carts):
                                        bet = table["players"][table["carts"]-1]['bet']
                                        msg = await bot.send_message(player['tele_id'],
                                            f"На кону: {ceiling}\
                                            \nКозырь: {trump}\
                                            \nВаши карты: {PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}\
                                            \nВыберите ставку:"+out,
                                            reply_markup = InlineKeyboardMarkup().add(
                                                InlineKeyboardButton(
                                                    text = "Уровнять",
                                                    callback_data = f"bet|{tableId}|equal|{old_bet}"
                                                ),
                                                InlineKeyboardButton(
                                                    text = "50",
                                                    callback_data = f"bet|{tableId}|50|{old_bet}"
                                                ),
                                                InlineKeyboardButton(
                                                    text = "100", 
                                                    callback_data = f"bet|{tableId}|100|{old_bet}"
                                                )
                                            )
                                        )  
                                        player["msg"] = msg
                                        player["old_bet"] = old_bet
                                        player["surplus_ceiling"] = old_bet
                                        name = table["players"][table["carts"]]["userNmae"]
                                        await bot.send_message(player['tele_id'],
                                            f"Сейчас ваш ход {name}",
                                            reply_markup = ReplyKeyboardMarkup().add(
                                                f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                                            ).row(
                                                "Фишек: " + str(balance)
                                            ).row(
                                                trump, str(ceiling)
                                            ).add(
                                                "Ваш ход (на него 25 секунд)"
                                            ).row(
                                                "Спасовать", "Выйти из игры"
                                            )
                                        )  
                                        table["players"][table["carts"]]["the_move_is_made"] = False
                                        loop.create_task(timeIsUp(msg, tableId, old_bet, table["carts"], table["m"]))




                                    if player["tele_id"] != int(carts):
                                        ссс = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                                        await bot.send_message(player['tele_id'],
                                            f'На кону: {ceiling}\
                                            \nКозырь: {trump}\
                                            \nВаши карты: {ссс}\
                                            \nОжидаем ставики другого игрока'+out,
                                        )
                                        name = table["players"][table["carts"]]["userNmae"]
                                        friend_id = table["players"][table["carts"]]["tele_id"]
                                        await bot.send_message(player['tele_id'],
                                            f"Сейчас ходит <a href=\"https://t.me/ppwweeqqbot?start=add_friend-{friend_id}-{name}\">{name}</a>",parse_mode="HTML",
                                            reply_markup = ReplyKeyboardMarkup().add(
                                                f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                                            ).row(
                                                "Фишек: " + str(balance)
                                            ).row(
                                                trump, str(ceiling)
                                            ).add(
                                                f"Ожидайем конца хода {name}"
                                            ).row(
                                                "Спасовать", "Выйти из игры"
                                            )
                                        )  
                                        

                            if equal == True:
                                ceiling = table["ceiling"]
                                
                                trump = PLAYING_CARDS_BTN_VALUE[table["trump"]]
                                table["carts"] = table["biggest_bet"][1]
                                carts = table["players"][table["carts"]]["tele_id"]
                                table["namePartGame"] = 2
                                for player in players:
                                    with connection.cursor() as cursor:
                                        request_tele_id = player["tele_id"]
                                        find_user = f"SELECT * FROM users WHERE tele_id = {request_tele_id};"
                                        cursor.execute(find_user)
                                        candidate = cursor.fetchone()
                                        balance = candidate["chips"]
                                    if player["tele_id"] == int(carts):
                                        msg = await bot.send_message(player['tele_id'],
                                            f"На кону: {ceiling}\
                                            \nКозырь: {trump}\
                                            \nВаши карты: {PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}\
                                            \nВыберите ставку:"+out,
                                            reply_markup = InlineKeyboardMarkup().add(
                                                InlineKeyboardButton(
                                                    text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]}",
                                                    callback_data = f"card|{tableId}|{player['cards'][0]}"
                                                ),
                                                InlineKeyboardButton(
                                                    text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][1]]}",
                                                    callback_data = f"card|{tableId}|{player['cards'][1]}"
                                                ),
                                                InlineKeyboardButton(
                                                    text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}",
                                                    callback_data = f"card|{tableId}|{player['cards'][2]}"
                                                )
                                            )
                                        )
                                        player["msg"] = msg
                                        name = table["players"][table["carts"]]["userNmae"]
                                        await bot.send_message(player['tele_id'],
                                            f"Сейчас ваш ход {name}",
                                            reply_markup = ReplyKeyboardMarkup().add(
                                                f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                                            ).row(
                                                "Фишек: " + str(balance)
                                            ).row(
                                                trump, str(ceiling)
                                            ).add(
                                                "Ваш ход (на него 25 секунд)"
                                            ).row(
                                                "Спасовать", "Выйти из игры"
                                            )
                                        ) 

                                        table["players"][table["carts"]]["the_move_is_made"] = False
                                        loop.create_task(timeIsUp(msg, tableId, 0, table["carts"], table["m"]))

                                    if player["tele_id"] != int(carts):
                                        await bot.send_message(player['tele_id'],
                                            f"На кону: {ceiling}\
                                            \nКозырь: {trump}\
                                            \nВаши карты: {PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]}  {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}\
                                            \nОжидаем хода другого игрока"+out,
                                        )
                                        name = table["players"][table["carts"]]["userNmae"]
                                        friend_id = table["players"][table["carts"]]["tele_id"]
                                        await bot.send_message(player['tele_id'],
                                            f"Сейчас ходит <a href=\"https://t.me/ppwweeqqbot?start=add_friend-{friend_id}-{name}\">{name}</a>",parse_mode="HTML",
                                            reply_markup = ReplyKeyboardMarkup().add(
                                                f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                                            ).row(
                                                "Фишек: " + str(balance)
                                            ).row(
                                                trump, str(ceiling)
                                            ).add(
                                                f"Ожидайем конца хода {name}"
                                            ).row(
                                                "Спасовать", "Выйти из игры"
                                            )
                                        )  

                        if table["namePartGame"] == 2:
                            for player in table["players"]:
                                if player["tele_id"] == message.from_user.id:
                                    outgoingPlayer = player
                                
                            
                            
                            table = games[tableId]
                            table["players"][table["carts"]]["the_move_is_made"] = True
                            out = ''
                            message_vin = ''
                            ceiling = table["ceiling"]
                            table["save_ceiling"] = ceiling
                            print(ceiling)
                            trump = PLAYING_CARDS_BTN_VALUE[table["trump"]]

                            players = []
                            noActivePlaers = []
                            for player in table["players"]:
                                if player['inGame'] == True:
                                    players.append(player)
                                if player['inGame'] == False:
                                    noActivePlaers.append(player)
                                    
                            
                            table["carts"] += 1
                            if table["carts"] > (len(table["players"])-1):
                                table["carts"] = 0
                            while table["players"][table["carts"]]['inGame'] == False:
                                table["carts"] += 1
                                if table["carts"] > (len(table["players"])-1):
                                    table["carts"] = 0

                            print(table["carts"])
                            table["turns"] += 1
                            strCardsOnTable = ""
                            strLastCard = ""
                            if len(players) <= table["turns"]:
                                vin = card_seniority(table["trump"], table["cards_on_table"][0], table["cards_on_table"])
                                for player in players:
                                    if player['thrownCard'] == vin:
                                        player['bribe'] += 1
                                        table["carts"] = table["players"].index(player)
                                        table["turns"] = 0
                                        table["partGame"] += 1
                                        table["cards_on_table"] = []
                                        message_vin = f"\nИгрок {player['userNmae']} выиграл взятку"

                            if len(table["cards_on_table"]) > 0:
                                strCardsOnTable = f"\nКарты на столе:"
                                for card in table["cards_on_table"]:
                                    strCardsOnTable = strCardsOnTable + ' ' + PLAYING_CARDS_BTN_VALUE[card]
                                lastCard = PLAYING_CARDS_BTN_VALUE[table["cards_on_table"][-1]]
                                strLastCard = f"\nПоследняя карта которую положили {lastCard}"
                            carts = table["players"][table["carts"]]["tele_id"]
                            if table["partGame"] < 3:
                                for player in players:
                                    with connection.cursor() as cursor:
                                        request_tele_id = player["tele_id"]
                                        find_user = f"SELECT * FROM users WHERE tele_id = {request_tele_id};"
                                        cursor.execute(find_user)
                                        candidate = cursor.fetchone()
                                        balance = candidate["chips"]
                                    print(table["cards_on_table"])
                                    if len(table["cards_on_table"]) != 0:
                                        cardss = permission_card(player['cards'], table["trump"], table["cards_on_table"][0])
                                    if len(table["cards_on_table"]) == 0:
                                        cardss = player['cards']
                                    if len(player['cards']) == 3:
                                        text = f"Ваши карты: {PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}" + strCardsOnTable + strLastCard
                                        if len(cardss) == 3:
                                            markup = InlineKeyboardMarkup().add(
                                                InlineKeyboardButton(
                                                    text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]}",
                                                    callback_data = f"card|{tableId}|{player['cards'][0]}"
                                                ),
                                                InlineKeyboardButton(
                                                    text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][1]]}",
                                                    callback_data = f"card|{tableId}|{player['cards'][1]}"
                                                ),
                                                InlineKeyboardButton(
                                                    text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}",
                                                    callback_data = f"card|{tableId}|{player['cards'][2]}"
                                                )
                                            )

                                        if len(cardss) == 2:
                                            markup = InlineKeyboardMarkup().add(
                                                InlineKeyboardButton(
                                                    text = f"{PLAYING_CARDS_BTN_VALUE[cardss[0]]}",
                                                    callback_data = f"card|{tableId}|{cardss[0]}"
                                                ),
                                                InlineKeyboardButton(
                                                    text = f"{PLAYING_CARDS_BTN_VALUE[cardss[1]]}",
                                                    callback_data = f"card|{tableId}|{cardss[1]}"
                                                )
                                            )
                                            
                                        if len(cardss) == 1:
                                            markup = InlineKeyboardMarkup().add(
                                                InlineKeyboardButton(
                                                    text = f"{PLAYING_CARDS_BTN_VALUE[cardss[0]]}",
                                                    callback_data = f"card|{tableId}|{cardss[0]}"
                                                )
                                            )




                                        rmarkup = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"

                                    if len(player['cards']) == 2:
                                        text = f"Ваши карты: {PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]}" + strCardsOnTable + strLastCard
                                        if len(cardss) == 2:
                                            markup = InlineKeyboardMarkup().add(
                                                InlineKeyboardButton(
                                                    text = f"{PLAYING_CARDS_BTN_VALUE[cardss[0]]}",
                                                    callback_data = f"card|{tableId}|{cardss[0]}"
                                                ),
                                                InlineKeyboardButton(
                                                    text = f"{PLAYING_CARDS_BTN_VALUE[cardss[1]]}",
                                                    callback_data = f"card|{tableId}|{cardss[1]}"
                                                )
                                            )
                                            
                                        if len(cardss) == 1:
                                            markup = InlineKeyboardMarkup().add(
                                                InlineKeyboardButton(
                                                    text = f"{PLAYING_CARDS_BTN_VALUE[cardss[0]]}",
                                                    callback_data = f"card|{tableId}|{cardss[0]}"
                                                )
                                            )
                                        rmarkup = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]}"

                                    if len(player['cards']) == 1:
                                        text = f"Ваши карты: {PLAYING_CARDS_BTN_VALUE[player['cards'][0]]}" + strCardsOnTable + strLastCard
                                        markup = InlineKeyboardMarkup().add(
                                            InlineKeyboardButton(
                                                text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]}",
                                                callback_data = f"card|{tableId}|{player['cards'][0]}"
                                            )
                                        )
                                        rmarkup = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} "

                                    if len(player['cards']) != 0:
                                        if player["tele_id"] == int(carts):
                                            msg = await bot.send_message(player['tele_id'],
                                                f"На кону: {ceiling}\
                                                \nКозырь: {trump}\n"+text+message_vin+out+"\nВыберите карту:",
                                                reply_markup = markup
                                            )
                                            player["msg"] = msg
                                            name = table["players"][table["carts"]]["userNmae"]
                                            await bot.send_message(player['tele_id'],
                                                f"Сейчас ваш ход {name}",
                                                reply_markup = ReplyKeyboardMarkup().add(
                                                    rmarkup
                                                ).row(
                                                    "Фишек: " + str(balance)
                                                ).row(
                                                    trump, str(ceiling)
                                                ).add(
                                                    "Ваш ход (на него 25 секунд)"
                                                ).row(
                                                    "Спасовать", "Выйти из игры"
                                                )
                                            ) 

                                            table["players"][table["carts"]]["the_move_is_made"] = False
                                            loop.create_task(timeIsUp(msg, tableId, 0, table["carts"], table["m"]))

                                        if player["tele_id"] != int(carts):
                                            await bot.send_message(player['tele_id'],
                                                f"На кону: {ceiling}\
                                                \nКозырь: {trump}\n"+text+message_vin+"\nОжидаем хода другого игрока"+out,
                                            )
                                            name = table["players"][table["carts"]]["userNmae"]
                                            friend_id = table["players"][table["carts"]]["tele_id"]
                                            await bot.send_message(player['tele_id'],
                                                f"Сейчас ходит <a href=\"https://t.me/ppwweeqqbot?start=add_friend-{friend_id}-{name}\">{name}</a>",parse_mode="HTML",
                                                reply_markup = ReplyKeyboardMarkup().add(
                                                    rmarkup
                                                ).row(
                                                    "Фишек: " + str(balance)
                                                ).row(
                                                    trump, str(ceiling)
                                                ).add(
                                                    f"Ожидайем конца хода {name}"
                                                ).row(
                                                    "Спасовать", "Выйти из игры"
                                                )
                                            ) 

                                    if len(player['cards']) == 0:
                                        text = f"Ваши карты закончились"+out
                                        if player["tele_id"] == int(carts):
                                            await bot.send_message(player['tele_id'],
                                                f"На кону: {ceiling}\
                                                \nКозырь: {trump}\n"+text+message_vin+out,
                                            )

                                        if player["tele_id"] != int(carts):
                                            await bot.send_message(player['tele_id'],
                                                f"На кону: {ceiling}\
                                                \nКозырь: {trump}\n"+strCardsOnTable+strLastCard+message_vin+out+"\nОжидаем хода другого игрока"+out,
                                            )   

                            if table["partGame"] == 3:
                                bigestBribe = 0
                                for player in players:
                                    if bigestBribe < player['bribe']:
                                        bigestBribe = player['bribe']
                                        winer = player['tele_id']
                                        winerName = player['userNmae']
                                    if player['bribe'] == 0:
                                        player['inGame'] = False
                                        player['azi'] = 1
                                
                                for player in table["players"]:
                                    if player['inGame'] == False:
                                        player['inAzi'] = True

                                if bigestBribe > 1 :
                                    with connection.cursor() as cursor:
                                        suma = int(table["ceiling"])/100*95
                                        requestDB = f"UPDATE users SET chips = (chips + {suma}) WHERE tele_id = {winer};"
                                        cursor.execute(requestDB)
                                        connection.commit()
                                    while len(table["wontin"]) != 0:
                                        table["players"].append(table["wontin"].pop(0))
                                    table["partGame"] = 0
                                    table["ceiling"] = 0
                                    table["trump"] = ''
                                    table["AZI"] = False
                                    table["CARDS_GAME"] = []
                                    table["biggest_bet"] = [0, 0]
                                    print(table)
                                    for player in table["players"]:
                                        player['inGame'] = True
                                        player['inAzi'] = False
                                        player['azi'] = 1
                                        player['bet'] = 0
                                        
                                    carts = table["players"][table["carts"]]["tele_id"]
                                    while len(table["wontin"]) != 0:
                                        table["players"].append(table["wontin"].pop(0))
                                        print(2111)
                                    
                                
                                    table["namePartGame"] = 2
                                    surplus_ceiling = 0



                                    table["CARDS_GAME"] = PLAYING_CARDS.copy()
                                    
                                    random.shuffle(table["CARDS_GAME"])
                                    for player in table["players"]:
                                        player['cards'].append(table["CARDS_GAME"].pop())
                                        player['cards'].append(table["CARDS_GAME"].pop())
                                        player['cards'].append(table["CARDS_GAME"].pop())

                                    table["trump"] = table["CARDS_GAME"].pop()
                                    trump = PLAYING_CARDS_BTN_VALUE[table["trump"]]
                                    for player in table["players"]:
                                        with connection.cursor() as cursor:
                                            request_tele_id = player["tele_id"]
                                            find_user = f"SELECT * FROM users WHERE tele_id = {request_tele_id};"
                                            cursor.execute(find_user)
                                            candidate = cursor.fetchone()
                                            balance = candidate["chips"]
                                    
                                        if player["tele_id"] == int(carts):
                                            bet = table["players"][table["carts"]-1]['bet']
                                            ccc = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                                            msg = await bot.send_message(player['tele_id'],
                                                f"Вы выиграли этот кон \
                                                \nВыберите ставку:",
                                                reply_markup = InlineKeyboardMarkup().add(
                                                    InlineKeyboardButton(
                                                        text = "50",
                                                        callback_data = f"bet|{tableId}|50|50"
                                                    ),
                                                    InlineKeyboardButton(
                                                        text = "100", 
                                                        callback_data = f"bet|{tableId}|100|100"
                                                    ),
                                                )
                                            )
                                            player["msg"] = msg
                                            player["surplus_ceiling"] = surplus_ceiling
                                            name = player["userNmae"]
                                            await bot.send_message(player['tele_id'],
                                                f"Сейчас ваш ход {name}",
                                                reply_markup = ReplyKeyboardMarkup().add(
                                                    ccc
                                                ).row(
                                                    "Фишек: " + str(balance)
                                                ).row(
                                                    trump, "0"
                                                ).add(
                                                    "Ваш ход (на него 25 секунд)"
                                                ).row(
                                                    "Спасовать", "Выйти из игры"
                                                )
                                            )

                                            table["players"][table["carts"]]["the_move_is_made"] = False
                                            loop.create_task(timeIsUp(msg, tableId, surplus_ceiling, table["carts"], table["m"]))


                                        
                                        if player["tele_id"] != int(carts):
                                            ccc = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                                            await bot.send_message(player['tele_id'],
                                                f"Игрок <a href=\"https://t.me/ppwweeqqbot?start=add_friend-{winer}-{winerName}\">{winerName}</a> выиграл кон\nОжидайте его ставики",
                                                parse_mode="HTML",
                                            )

                                            name = table["players"][table["carts"]]["userNmae"]
                                            friend_id = table["players"][table["carts"]]["tele_id"] 
                                            await bot.send_message(player['tele_id'],
                                                f"Сейчас ходит <a href=\"https://t.me/ppwweeqqbot?start=add_friend-{friend_id}-{name}\">{name}</a>",parse_mode="HTML",
                                                reply_markup = ReplyKeyboardMarkup().add(
                                                    ccc
                                                ).row(
                                                    "Фишек: " + str(balance)
                                                ).row(
                                                    trump, "0"
                                                ).add(
                                                    f"Ожидайем конца хода {name}"
                                                ).row(
                                                    "Спасовать", "Выйти из игры"
                                                )
                                            )


                                    
                                if bigestBribe <= 1 :
                                    table["AZI"] = True
                                    players = []
                                    noActivePlaers = []
                                    for player in table["players"]:
                                        if player['inAzi'] == False:
                                            players.append(player)
                                        if player['inAzi'] == True:
                                            noActivePlaers.append(player)
                                            
                                    carts = noActivePlaers[0]["tele_id"]
                                    for player in noActivePlaers:
                                        if player["tele_id"] == int(carts):
                                            if player['azi'] == 1:
                                                prise = ceiling/2
                                                msg = await bot.send_message(player['tele_id'],
                                                    f"На кону: {ceiling}\
                                                    \nВвариться в АЗИ ценой: фишек {prise}",
                                                    reply_markup = InlineKeyboardMarkup().add(
                                                        InlineKeyboardButton(
                                                            text = f"Да",
                                                            callback_data = f"azi|{tableId}|yes|1"
                                                        ),
                                                        InlineKeyboardButton(
                                                            text = f"Нет",
                                                            callback_data = f"azi|{tableId}|not"
                                                        )
                                                    )
                                                )
                                            if player['azi'] == 2:
                                                msg = await bot.send_message(player['tele_id'],
                                                    f"На кону: {ceiling}\
                                                    \nВвариться в АЗИ ценой: фишек {ceiling}",
                                                    reply_markup = InlineKeyboardMarkup().add(
                                                        InlineKeyboardButton(
                                                            text = f"Да",
                                                            callback_data = f"azi|{tableId}|yes|2"
                                                        ),
                                                        InlineKeyboardButton(
                                                            text = f"Нет",
                                                            callback_data = f"azi|{tableId}|not"
                                                        )
                                                    )
                                                )

                                        if player["tele_id"] != int(carts):
                                            await bot.send_message(player['tele_id'],
                                                f"Ожидаем выбора других игроков",
                                            )
                                    
                                    for player in table["players"]:
                                        if player["tele_id"] == int(carts):
                                            player["carts_azi"] = True
                                            player["azi_msg"] = msg
                                            print(msg)
                                            print('msg')
                                            print(player["azi_msg"])
                                            print('player["azi_msg"]')

                                    for player in players:
                                        await bot.send_message(player['tele_id'],
                                            f"Ожидаем выбора других игроков",
                                        )
                        
    
                  

           
        
                
async def quitOfGame(message: types.Message, state):
    async with state.proxy() as data:
        tableId = data['hostId']
        type = data['type']
        
    if type == 0:
        table = games[tableId]
    if type == 1:
        table = publickGames[tableId]
    table["m"] += 1
    for index, player in  enumerate(table["players"]):
        if player["tele_id"] == message.from_user.id:
            indexPl = index
            break
    if table["players"][indexPl]['tele_id'] == table["players"][table["carts"]]['tele_id']:
        await bot.delete_message(
            chat_id=table["players"][indexPl]["msg"].chat.id, 
            message_id=table["players"][indexPl]["msg"].message_id
        )
        surplus_ceiling = player["surplus_ceiling"]
        old_bet = surplus_ceiling
    
    
    if len(table["players"]) <= 2:
        for player in table["players"]:
            if player['tele_id'] != message.from_user.id:
                await bot.send_message(player['tele_id'],
                    "Все покинули игру, игра закончилась ",
                    reply_markup = mein_menu_markup
                ) 
            
            with connection.cursor() as cursor:
                requestDB = f"UPDATE users SET in_game = 0 WHERE tele_id = {player['tele_id']};"
                cursor.execute(requestDB)
                connection.commit()
        if type == 0:
            del games[tableId]
        if type == 1:
            del publickGames[tableId]
            
            
    
    if len(table["players"]) > 2:  
        if table["AZI"] == True:
            for player in table["players"]:
                if player["tele_id"] == message.from_user.id:
                    print(player["azi_msg"])
                    print(player["azi_msg"]["message_id"])
                    print(player["azi_msg"]["chat"]["id"])
                    if player["carts_azi"] == True:
                        # await bot.delete_message(chat_id=player["azi_msg"]["chat"]["id"], message_id=player["azi_msg"]["message_id"])
                        players = []
                        ceiling = table["ceiling"]
                        save_ceiling = table["save_ceiling"]
                        
                        
                        for player in table["players"]:
                            if player['inAzi'] == True:
                                players.append(player)


                        carts = players[0]["tele_id"]
                        for player in table["players"]:
                            if player["tele_id"] == carts:
                                player['inGame'] = False
                                player['inAzi'] = False
                                
                        players = []
                        for player in table["players"]:
                            if player['inAzi'] == True:
                                players.append(player)

                        if len(players) != 0:
                            carts = players[0]["tele_id"]
                            for player in table["players"]:
                                if player["tele_id"] == int(carts):
                                    player["carts_azi"] = True
                            for player in players:
                                if player["tele_id"] == int(carts):
                                    if player['azi'] == 1:
                                        prise = ceiling/2
                                        msg = await bot.send_message(player['tele_id'],
                                            f"На кону: {ceiling}\
                                            \nВвариться в АЗИ ценой: фишек {prise}",
                                            reply_markup = InlineKeyboardMarkup().add(
                                                InlineKeyboardButton(
                                                    text = f"Да",
                                                    callback_data = f"azi|{tableId}|yes|1"
                                                ),
                                                InlineKeyboardButton(
                                                    text = f"Нет",
                                                    callback_data = f"azi|{tableId}|not"
                                                )
                                            )
                                        )
                                    if player['azi'] == 2:
                                        msg = await bot.send_message(player['tele_id'],
                                            f"На кону: {ceiling}\
                                            \nВвариться в АЗИ ценой: фишек {ceiling}",
                                            reply_markup = InlineKeyboardMarkup().add(
                                                InlineKeyboardButton(
                                                    text = f"Да",
                                                    callback_data = f"azi|{tableId}|yes|2"
                                                ),
                                                InlineKeyboardButton(
                                                    text = f"Нет",
                                                    callback_data = f"azi|{tableId}|not"
                                                )
                                            )
                                        )  
                                    
                                for player in table["players"]:
                                    if player["tele_id"] == int(carts):
                                        player["carts_azi"] = True
                                        player["azi_msg"] = msg

                        if len(players) == 0:   
                            players = []
                            for player in table["players"]:
                                if player['inGame'] == True:
                                    player['inAzi'] == False
                                    players.append(player)
                            table["turns"] = 0
                            table["partGame"] = 0
                            table["CARDS_GAME"] = PLAYING_CARDS.copy()
                            random.shuffle(table["CARDS_GAME"])
                            for player in players:
                                player['cards'].append(table["CARDS_GAME"].pop())
                                player['cards'].append(table["CARDS_GAME"].pop())
                                player['cards'].append(table["CARDS_GAME"].pop())
                            
                            ceiling = table["ceiling"]
                            table["trump"] = table["CARDS_GAME"].pop()
                            trump = PLAYING_CARDS_BTN_VALUE[table["trump"]]
                            carts = table["players"][table["carts"]]['tele_id']
                            for player in players:
                                with connection.cursor() as cursor:
                                    request_tele_id = player["tele_id"]
                                    find_user = f"SELECT * FROM users WHERE tele_id = {request_tele_id};"
                                    cursor.execute(find_user)
                                    candidate = cursor.fetchone()
                                    balance = candidate["chips"]
                                if player["tele_id"] == int(carts):
                                    await bot.send_message(player['tele_id'],
                                        f"На кону: {ceiling}\
                                        \nКозырь: {trump}\
                                        \nВаши карты: {PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}\
                                        \nВыберите карту:",
                                        reply_markup = InlineKeyboardMarkup().add(
                                            InlineKeyboardButton(
                                                text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]}",
                                                callback_data = f"card|{tableId}|{player['cards'][0]}"
                                            ),
                                            InlineKeyboardButton(
                                                text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][1]]}",
                                                callback_data = f"card|{tableId}|{player['cards'][1]}"
                                            ),
                                            InlineKeyboardButton(
                                                text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}",
                                                callback_data = f"card|{tableId}|{player['cards'][2]}"
                                            )
                                        )
                                    ) 
                                    ccc = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                                    name = table["players"][table["carts"]]["userNmae"]
                                    await bot.send_message(player['tele_id'],
                                        f"Сейчас ваш ход {name}",
                                        reply_markup = ReplyKeyboardMarkup().add(
                                            ccc
                                        ).row(
                                            "Фишек: " + str(balance)
                                        ).row(
                                            trump, str(ceiling)
                                        ).add(
                                            "Ваш ход (на него 25 секунд)"
                                        ).row(
                                            "Спасовать", "Выйти из игры"
                                        )
                                    )


                                if player["tele_id"] != int(carts):
                                    await bot.send_message(player['tele_id'],
                                        f"На кону: {ceiling}\
                                        \nКозырь: {trump}\
                                        \nВаши карты: {PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}\
                                        \nОжидаем хода другого игрока",
                                    )
                                    name = table["players"][table["carts"]]['userNmae']
                                    friend_id = table["players"][table["carts"]]["tele_id"]
                                    ccc = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                                    await bot.send_message(player['tele_id'],
                                            f"Сейчас ходит <a href=\"https://t.me/ppwweeqqbot?start=add_friend-{friend_id}-{name}\">{name}</a>",parse_mode="HTML",
                                        reply_markup = ReplyKeyboardMarkup().add(
                                            ccc
                                        ).row(
                                            "Фишек: " + str(balance)
                                        ).row(
                                            trump, str(ceiling)
                                        ).add(
                                            f"Ожидайем конца хода {name}"
                                        ).row(
                                            "Спасовать", "Выйти из игры"
                                        )
                                    )
             
        if table["AZI"] == False:
            if table["players"][indexPl]['tele_id'] == table["players"][table["carts"]]['tele_id']:
                if table["namePartGame"] == 1:
                    for player in table["players"]:
                        if player["tele_id"] == message.from_user.id:
                            outgoingPlayer = player
                    
                    print(outgoingPlayer['msg'])        
                    print(outgoingPlayer['msg']["chat"]["id"])        
                    print('msg')        
                    # print(outgoingPlayer['msg']["reply_markup"]["inline_keyboard"][0]["callback_data"])        
                    # print(outgoingPlayer['msg']["reply_markup"]["inline_keyboard"][0])        
                    print("inline_keyboard")           
                    print(outgoingPlayer['msg']["reply_markup"]["inline_keyboard"])           
                    
                    table["players"][table["carts"]]["the_move_is_made"] = True
                    players = []
                    noActivePlaers = []
                    out = ''
                    old_bet = outgoingPlayer["old_bet"] 
                        
                    if table["biggest_bet"][0] < table["players"][table["carts"]]['bet']:
                        table["biggest_bet"][0] = copy.copy(table["players"][table["carts"]]['bet'])
                        table["biggest_bet"][1] = copy.copy(table["carts"])

                    for player in table["players"]:
                        if player['inGame'] == True:
                            players.append(player)
                        if player['inGame'] == False:
                            noActivePlaers.append(player)


                    table["carts"] += 1
                    if table["carts"] > (len(table["players"])-1):
                        table["carts"] = 0
                    while table["players"][table["carts"]]['inGame'] == False:
                        table["carts"] += 1
                        if table["carts"] > (len(table["players"])-1):
                            table["carts"] = 0
                    carts = table["players"][table["carts"]]["tele_id"]
                    equal = check_equalities(players)


                    if equal == False:
                        ceiling = table["ceiling"]
                        
                        trump = PLAYING_CARDS_BTN_VALUE[table["trump"]]
                        for player in players:
                            with connection.cursor() as cursor:
                                request_tele_id = player["tele_id"]
                                find_user = f"SELECT * FROM users WHERE tele_id = {request_tele_id};"
                                cursor.execute(find_user)
                                candidate = cursor.fetchone()
                                balance = candidate["chips"]
                            if player["tele_id"] == int(carts):
                                bet = table["players"][table["carts"]-1]['bet']
                                msg = await bot.send_message(player['tele_id'],
                                    f"На кону: {ceiling}\
                                    \nКозырь: {trump}\
                                    \nВаши карты: {PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}\
                                    \nВыберите ставку:"+out,
                                    reply_markup = InlineKeyboardMarkup().add(
                                        InlineKeyboardButton(
                                            text = "Уровнять",
                                            callback_data = f"bet|{tableId}|equal|{old_bet}"
                                        ),
                                        InlineKeyboardButton(
                                            text = "50",
                                            callback_data = f"bet|{tableId}|50|{old_bet}"
                                        ),
                                        InlineKeyboardButton(
                                            text = "100", 
                                            callback_data = f"bet|{tableId}|100|{old_bet}"
                                        )
                                    )
                                )  
                                player["msg"] = msg
                                player["old_bet"] = old_bet
                                player["surplus_ceiling"] = old_bet
                                name = table["players"][table["carts"]]["userNmae"]
                                await bot.send_message(player['tele_id'],
                                    f"Сейчас ваш ход {name}",
                                    reply_markup = ReplyKeyboardMarkup().add(
                                        f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                                    ).row(
                                        "Фишек: " + str(balance)
                                    ).row(
                                        trump, str(ceiling)
                                    ).add(
                                        "Ваш ход (на него 25 секунд)"
                                    ).row(
                                        "Спасовать", "Выйти из игры"
                                    )
                                )  
                                table["players"][table["carts"]]["the_move_is_made"] = False
                                loop.create_task(timeIsUp(msg, tableId, old_bet, table["carts"], table["m"]))




                            if player["tele_id"] != int(carts):
                                ссс = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                                await bot.send_message(player['tele_id'],
                                    f'На кону: {ceiling}\
                                    \nКозырь: {trump}\
                                    \nВаши карты: {ссс}\
                                    \nОжидаем ставики другого игрока'+out,
                                )
                                name = table["players"][table["carts"]]["userNmae"]
                                friend_id = table["players"][table["carts"]]["tele_id"]
                                await bot.send_message(player['tele_id'],
                                    f"Сейчас ходит <a href=\"https://t.me/ppwweeqqbot?start=add_friend-{friend_id}-{name}\">{name}</a>",parse_mode="HTML",
                                    reply_markup = ReplyKeyboardMarkup().add(
                                        f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                                    ).row(
                                        "Фишек: " + str(balance)
                                    ).row(
                                        trump, str(ceiling)
                                    ).add(
                                        f"Ожидайем конца хода {name}"
                                    ).row(
                                        "Спасовать", "Выйти из игры"
                                    )
                                )  
                                

                    if equal == True:
                        ceiling = table["ceiling"]
                        
                        trump = PLAYING_CARDS_BTN_VALUE[table["trump"]]
                        table["carts"] = table["biggest_bet"][1]
                        carts = table["players"][table["carts"]]["tele_id"]
                        table["namePartGame"] = 2
                        for player in players:
                            with connection.cursor() as cursor:
                                request_tele_id = player["tele_id"]
                                find_user = f"SELECT * FROM users WHERE tele_id = {request_tele_id};"
                                cursor.execute(find_user)
                                candidate = cursor.fetchone()
                                balance = candidate["chips"]
                            if player["tele_id"] == int(carts):
                                msg = await bot.send_message(player['tele_id'],
                                    f"На кону: {ceiling}\
                                    \nКозырь: {trump}\
                                    \nВаши карты: {PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}\
                                    \nВыберите ставку:"+out,
                                    reply_markup = InlineKeyboardMarkup().add(
                                        InlineKeyboardButton(
                                            text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]}",
                                            callback_data = f"card|{tableId}|{player['cards'][0]}"
                                        ),
                                        InlineKeyboardButton(
                                            text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][1]]}",
                                            callback_data = f"card|{tableId}|{player['cards'][1]}"
                                        ),
                                        InlineKeyboardButton(
                                            text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}",
                                            callback_data = f"card|{tableId}|{player['cards'][2]}"
                                        )
                                    )
                                )
                                player["msg"] = msg
                                name = table["players"][table["carts"]]["userNmae"]
                                await bot.send_message(player['tele_id'],
                                    f"Сейчас ваш ход {name}",
                                    reply_markup = ReplyKeyboardMarkup().add(
                                        f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                                    ).row(
                                        "Фишек: " + str(balance)
                                    ).row(
                                        trump, str(ceiling)
                                    ).add(
                                        "Ваш ход (на него 25 секунд)"
                                    ).row(
                                        "Спасовать", "Выйти из игры"
                                    )
                                ) 

                                table["players"][table["carts"]]["the_move_is_made"] = False
                                loop.create_task(timeIsUp(msg, tableId, 0, table["carts"], table["m"]))

                            if player["tele_id"] != int(carts):
                                await bot.send_message(player['tele_id'],
                                    f"На кону: {ceiling}\
                                    \nКозырь: {trump}\
                                    \nВаши карты: {PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]}  {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}\
                                    \nОжидаем хода другого игрока"+out,
                                )
                                name = table["players"][table["carts"]]["userNmae"]
                                friend_id = table["players"][table["carts"]]["tele_id"]
                                await bot.send_message(player['tele_id'],
                                    f"Сейчас ходит <a href=\"https://t.me/ppwweeqqbot?start=add_friend-{friend_id}-{name}\">{name}</a>",parse_mode="HTML",
                                    reply_markup = ReplyKeyboardMarkup().add(
                                        f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                                    ).row(
                                        "Фишек: " + str(balance)
                                    ).row(
                                        trump, str(ceiling)
                                    ).add(
                                        f"Ожидайем конца хода {name}"
                                    ).row(
                                        "Спасовать", "Выйти из игры"
                                    )
                                )  

                if table["namePartGame"] == 2:
                    for player in table["players"]:
                        if player["tele_id"] == message.from_user.id:
                            outgoingPlayer = player
                           
                    
                    
                    table = games[tableId]
                    table["players"][table["carts"]]["the_move_is_made"] = True
                    out = ''
                    message_vin = ''
                    ceiling = table["ceiling"]
                    table["save_ceiling"] = ceiling
                    print(ceiling)
                    trump = PLAYING_CARDS_BTN_VALUE[table["trump"]]

                    players = []
                    noActivePlaers = []
                    for player in table["players"]:
                        if player['inGame'] == True:
                            players.append(player)
                        if player['inGame'] == False:
                            noActivePlaers.append(player)
                            
                    
                    table["carts"] += 1
                    if table["carts"] > (len(table["players"])-1):
                        table["carts"] = 0
                    while table["players"][table["carts"]]['inGame'] == False:
                        table["carts"] += 1
                        if table["carts"] > (len(table["players"])-1):
                            table["carts"] = 0

                    print(table["carts"])
                    table["turns"] += 1
                    strCardsOnTable = ""
                    strLastCard = ""
                    if len(players) <= table["turns"]:
                        vin = card_seniority(table["trump"], table["cards_on_table"][0], table["cards_on_table"])
                        for player in players:
                            if player['thrownCard'] == vin:
                                player['bribe'] += 1
                                table["carts"] = table["players"].index(player)
                                table["turns"] = 0
                                table["partGame"] += 1
                                table["cards_on_table"] = []
                                message_vin = f"\nИгрок {player['userNmae']} выиграл взятку"

                    if len(table["cards_on_table"]) > 0:
                        strCardsOnTable = f"\nКарты на столе:"
                        for card in table["cards_on_table"]:
                            strCardsOnTable = strCardsOnTable + ' ' + PLAYING_CARDS_BTN_VALUE[card]
                        lastCard = PLAYING_CARDS_BTN_VALUE[table["cards_on_table"][-1]]
                        strLastCard = f"\nПоследняя карта которую положили {lastCard}"
                    carts = table["players"][table["carts"]]["tele_id"]
                    if table["partGame"] < 3:
                        for player in players:
                            with connection.cursor() as cursor:
                                request_tele_id = player["tele_id"]
                                find_user = f"SELECT * FROM users WHERE tele_id = {request_tele_id};"
                                cursor.execute(find_user)
                                candidate = cursor.fetchone()
                                balance = candidate["chips"]
                            print(table["cards_on_table"])
                            if len(table["cards_on_table"]) != 0:
                                cardss = permission_card(player['cards'], table["trump"], table["cards_on_table"][0])
                            if len(table["cards_on_table"]) == 0:
                                cardss = player['cards']
                            if len(player['cards']) == 3:
                                text = f"Ваши карты: {PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}" + strCardsOnTable + strLastCard
                                if len(cardss) == 3:
                                    markup = InlineKeyboardMarkup().add(
                                        InlineKeyboardButton(
                                            text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]}",
                                            callback_data = f"card|{tableId}|{player['cards'][0]}"
                                        ),
                                        InlineKeyboardButton(
                                            text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][1]]}",
                                            callback_data = f"card|{tableId}|{player['cards'][1]}"
                                        ),
                                        InlineKeyboardButton(
                                            text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}",
                                            callback_data = f"card|{tableId}|{player['cards'][2]}"
                                        )
                                    )

                                if len(cardss) == 2:
                                    markup = InlineKeyboardMarkup().add(
                                        InlineKeyboardButton(
                                            text = f"{PLAYING_CARDS_BTN_VALUE[cardss[0]]}",
                                            callback_data = f"card|{tableId}|{cardss[0]}"
                                        ),
                                        InlineKeyboardButton(
                                            text = f"{PLAYING_CARDS_BTN_VALUE[cardss[1]]}",
                                            callback_data = f"card|{tableId}|{cardss[1]}"
                                        )
                                    )
                                    
                                if len(cardss) == 1:
                                    markup = InlineKeyboardMarkup().add(
                                        InlineKeyboardButton(
                                            text = f"{PLAYING_CARDS_BTN_VALUE[cardss[0]]}",
                                            callback_data = f"card|{tableId}|{cardss[0]}"
                                        )
                                    )




                                rmarkup = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"

                            if len(player['cards']) == 2:
                                text = f"Ваши карты: {PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]}" + strCardsOnTable + strLastCard
                                if len(cardss) == 2:
                                    markup = InlineKeyboardMarkup().add(
                                        InlineKeyboardButton(
                                            text = f"{PLAYING_CARDS_BTN_VALUE[cardss[0]]}",
                                            callback_data = f"card|{tableId}|{cardss[0]}"
                                        ),
                                        InlineKeyboardButton(
                                            text = f"{PLAYING_CARDS_BTN_VALUE[cardss[1]]}",
                                            callback_data = f"card|{tableId}|{cardss[1]}"
                                        )
                                    )
                                    
                                if len(cardss) == 1:
                                    markup = InlineKeyboardMarkup().add(
                                        InlineKeyboardButton(
                                            text = f"{PLAYING_CARDS_BTN_VALUE[cardss[0]]}",
                                            callback_data = f"card|{tableId}|{cardss[0]}"
                                        )
                                    )
                                rmarkup = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]}"

                            if len(player['cards']) == 1:
                                text = f"Ваши карты: {PLAYING_CARDS_BTN_VALUE[player['cards'][0]]}" + strCardsOnTable + strLastCard
                                markup = InlineKeyboardMarkup().add(
                                    InlineKeyboardButton(
                                        text = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]}",
                                        callback_data = f"card|{tableId}|{player['cards'][0]}"
                                    )
                                )
                                rmarkup = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} "

                            if len(player['cards']) != 0:
                                if player["tele_id"] == int(carts):
                                    msg = await bot.send_message(player['tele_id'],
                                        f"На кону: {ceiling}\
                                        \nКозырь: {trump}\n"+text+message_vin+out+"\nВыберите карту:",
                                        reply_markup = markup
                                    )
                                    player["msg"] = msg
                                    name = table["players"][table["carts"]]["userNmae"]
                                    await bot.send_message(player['tele_id'],
                                        f"Сейчас ваш ход {name}",
                                        reply_markup = ReplyKeyboardMarkup().add(
                                            rmarkup
                                        ).row(
                                            "Фишек: " + str(balance)
                                        ).row(
                                            trump, str(ceiling)
                                        ).add(
                                            "Ваш ход (на него 25 секунд)"
                                        ).row(
                                            "Спасовать", "Выйти из игры"
                                        )
                                    ) 

                                    table["players"][table["carts"]]["the_move_is_made"] = False
                                    loop.create_task(timeIsUp(msg, tableId, 0, table["carts"], table["m"]))

                                if player["tele_id"] != int(carts):
                                    await bot.send_message(player['tele_id'],
                                        f"На кону: {ceiling}\
                                        \nКозырь: {trump}\n"+text+message_vin+"\nОжидаем хода другого игрока"+out,
                                    )
                                    name = table["players"][table["carts"]]["userNmae"]
                                    friend_id = table["players"][table["carts"]]["tele_id"]
                                    await bot.send_message(player['tele_id'],
                                        f"Сейчас ходит <a href=\"https://t.me/ppwweeqqbot?start=add_friend-{friend_id}-{name}\">{name}</a>",parse_mode="HTML",
                                        reply_markup = ReplyKeyboardMarkup().add(
                                            rmarkup
                                        ).row(
                                            "Фишек: " + str(balance)
                                        ).row(
                                            trump, str(ceiling)
                                        ).add(
                                            f"Ожидайем конца хода {name}"
                                        ).row(
                                            "Спасовать", "Выйти из игры"
                                        )
                                    ) 

                            if len(player['cards']) == 0:
                                text = f"Ваши карты закончились"+out
                                if player["tele_id"] == int(carts):
                                    await bot.send_message(player['tele_id'],
                                        f"На кону: {ceiling}\
                                        \nКозырь: {trump}\n"+text+message_vin+out,
                                    )

                                if player["tele_id"] != int(carts):
                                    await bot.send_message(player['tele_id'],
                                        f"На кону: {ceiling}\
                                        \nКозырь: {trump}\n"+strCardsOnTable+strLastCard+message_vin+out+"\nОжидаем хода другого игрока"+out,
                                    )   

                    if table["partGame"] == 3:
                        bigestBribe = 0
                        for player in players:
                            if bigestBribe < player['bribe']:
                                bigestBribe = player['bribe']
                                winer = player['tele_id']
                                winerName = player['userNmae']
                            if player['bribe'] == 0:
                                player['inGame'] = False
                                player['azi'] = 1
                        
                        for player in table["players"]:
                            if player['inGame'] == False:
                                player['inAzi'] = True

                        if bigestBribe > 1 :
                            with connection.cursor() as cursor:
                                suma = int(table["ceiling"])/100*95
                                requestDB = f"UPDATE users SET chips = (chips + {suma}) WHERE tele_id = {winer};"
                                cursor.execute(requestDB)
                                connection.commit()
                            while len(table["wontin"]) != 0:
                                table["players"].append(table["wontin"].pop(0))
                            table["partGame"] = 0
                            table["ceiling"] = 0
                            table["trump"] = ''
                            table["AZI"] = False
                            table["CARDS_GAME"] = []
                            table["biggest_bet"] = [0, 0]
                            print(table)
                            for player in table["players"]:
                                player['inGame'] = True
                                player['inAzi'] = False
                                player['azi'] = 1
                                player['bet'] = 0
                                
                            carts = table["players"][table["carts"]]["tele_id"]
                            while len(table["wontin"]) != 0:
                                table["players"].append(table["wontin"].pop(0))
                                print(2111)
                            
                        
                            table["namePartGame"] = 2
                            surplus_ceiling = 0



                            table["CARDS_GAME"] = PLAYING_CARDS.copy()
                            
                            random.shuffle(table["CARDS_GAME"])
                            for player in table["players"]:
                                player['cards'].append(table["CARDS_GAME"].pop())
                                player['cards'].append(table["CARDS_GAME"].pop())
                                player['cards'].append(table["CARDS_GAME"].pop())

                            table["trump"] = table["CARDS_GAME"].pop()
                            trump = PLAYING_CARDS_BTN_VALUE[table["trump"]]
                            for player in table["players"]:
                                with connection.cursor() as cursor:
                                    request_tele_id = player["tele_id"]
                                    find_user = f"SELECT * FROM users WHERE tele_id = {request_tele_id};"
                                    cursor.execute(find_user)
                                    candidate = cursor.fetchone()
                                    balance = candidate["chips"]
                            
                                if player["tele_id"] == int(carts):
                                    bet = table["players"][table["carts"]-1]['bet']
                                    ccc = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                                    msg = await bot.send_message(player['tele_id'],
                                        f"Вы выиграли этот кон \
                                        \nВыберите ставку:",
                                        reply_markup = InlineKeyboardMarkup().add(
                                            InlineKeyboardButton(
                                                text = "50",
                                                callback_data = f"bet|{tableId}|50|50"
                                            ),
                                            InlineKeyboardButton(
                                                text = "100", 
                                                callback_data = f"bet|{tableId}|100|100"
                                            ),
                                        )
                                    )
                                    player["msg"] = msg
                                    player["surplus_ceiling"] = surplus_ceiling
                                    name = player["userNmae"]
                                    await bot.send_message(player['tele_id'],
                                        f"Сейчас ваш ход {name}",
                                        reply_markup = ReplyKeyboardMarkup().add(
                                            ccc
                                        ).row(
                                            "Фишек: " + str(balance)
                                        ).row(
                                            trump, "0"
                                        ).add(
                                            "Ваш ход (на него 25 секунд)"
                                        ).row(
                                            "Спасовать", "Выйти из игры"
                                        )
                                    )

                                    table["players"][table["carts"]]["the_move_is_made"] = False
                                    loop.create_task(timeIsUp(msg, tableId, surplus_ceiling, table["carts"], table["m"]))


                                
                                if player["tele_id"] != int(carts):
                                    ccc = f"{PLAYING_CARDS_BTN_VALUE[player['cards'][0]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][1]]} {PLAYING_CARDS_BTN_VALUE[player['cards'][2]]}"
                                    await bot.send_message(player['tele_id'],
                                        f"Игрок <a href=\"https://t.me/ppwweeqqbot?start=add_friend-{winer}-{winerName}\">{winerName}</a> выиграл кон\nОжидайте его ставики",
                                        parse_mode="HTML",
                                    )

                                    name = table["players"][table["carts"]]["userNmae"]
                                    friend_id = table["players"][table["carts"]]["tele_id"] 
                                    await bot.send_message(player['tele_id'],
                                        f"Сейчас ходит <a href=\"https://t.me/ppwweeqqbot?start=add_friend-{friend_id}-{name}\">{name}</a>",parse_mode="HTML",
                                        reply_markup = ReplyKeyboardMarkup().add(
                                            ccc
                                        ).row(
                                            "Фишек: " + str(balance)
                                        ).row(
                                            trump, "0"
                                        ).add(
                                            f"Ожидайем конца хода {name}"
                                        ).row(
                                            "Спасовать", "Выйти из игры"
                                        )
                                    )


                            
                        if bigestBribe <= 1 :
                            table["AZI"] = True
                            players = []
                            noActivePlaers = []
                            for player in table["players"]:
                                if player['inAzi'] == False:
                                    players.append(player)
                                if player['inAzi'] == True:
                                    noActivePlaers.append(player)
                                    
                            carts = noActivePlaers[0]["tele_id"]
                            for player in noActivePlaers:
                                if player["tele_id"] == int(carts):
                                    if player['azi'] == 1:
                                        prise = ceiling/2
                                        msg = await bot.send_message(player['tele_id'],
                                            f"На кону: {ceiling}\
                                            \nВвариться в АЗИ ценой: фишек {prise}",
                                            reply_markup = InlineKeyboardMarkup().add(
                                                InlineKeyboardButton(
                                                    text = f"Да",
                                                    callback_data = f"azi|{tableId}|yes|1"
                                                ),
                                                InlineKeyboardButton(
                                                    text = f"Нет",
                                                    callback_data = f"azi|{tableId}|not"
                                                )
                                            )
                                        )
                                    if player['azi'] == 2:
                                        msg = await bot.send_message(player['tele_id'],
                                            f"На кону: {ceiling}\
                                            \nВвариться в АЗИ ценой: фишек {ceiling}",
                                            reply_markup = InlineKeyboardMarkup().add(
                                                InlineKeyboardButton(
                                                    text = f"Да",
                                                    callback_data = f"azi|{tableId}|yes|2"
                                                ),
                                                InlineKeyboardButton(
                                                    text = f"Нет",
                                                    callback_data = f"azi|{tableId}|not"
                                                )
                                            )
                                        )

                                if player["tele_id"] != int(carts):
                                    await bot.send_message(player['tele_id'],
                                        f"Ожидаем выбора других игроков",
                                    )
                            
                            for player in table["players"]:
                                if player["tele_id"] == int(carts):
                                    player["carts_azi"] = True
                                    player["azi_msg"] = msg
                                    print(msg)
                                    print('msg')
                                    print(player["azi_msg"])
                                    print('player["azi_msg"]')

                            for player in players:
                                await bot.send_message(player['tele_id'],
                                    f"Ожидаем выбора других игроков",
                                )
                

    
    table["players"].pop(indexPl)
    await bot.send_message(message.from_user.id,
        "Вы вышли из игры",
        reply_markup = mein_menu_markup
    ) 
    
    with connection.cursor() as cursor:
        requestDB = f"UPDATE users SET in_game = 0 WHERE tele_id = {message.from_user.id};"
        cursor.execute(requestDB)
        connection.commit() 
    

def game_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(start_game, text_contains="start_game" )
    dp.register_callback_query_handler(set_bet, text_contains="bet" )
    dp.register_callback_query_handler(card_game, text_contains="card" )
    dp.register_callback_query_handler(azi, text_contains="azi" )
    dp.register_message_handler(quitOfTable, lambda msg: msg.text == "Спасовать" )
    dp.register_message_handler(quitOfGame, lambda msg: msg.text == "Выйти из игры" )