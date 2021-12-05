from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup


start_game_markup = InlineKeyboardMarkup().add(
    InlineKeyboardButton(
        text = "На фишки",
        callback_data = f"valuta|chips"
    ),
    InlineKeyboardButton(
        text = "На деньги(пока не работает)", 
        callback_data = f"valuta|cash"
    )
).add(
    InlineKeyboardButton(
        text = "Отмена", 
        callback_data = f"abolition"
    )
)


tables_markup = InlineKeyboardMarkup().add(
    InlineKeyboardButton(
        text = "Создать публичный стол",
        callback_data = f"public_table_players_number"
    )
).add(
    InlineKeyboardButton(
        text = "Присоединиться к публичному столу", 
        callback_data = f"zxc_public_table"
    )
).add(
    InlineKeyboardButton(
        text = "Создать приватный стол", 
        callback_data = f"private_table_players_number"
    )
).add(
    InlineKeyboardButton(
        text = "Отмена", 
        callback_data = f"abolition"
    )
)



value_plaears_private_markup = InlineKeyboardMarkup().add(
    InlineKeyboardButton(
        text = "2",
        callback_data = f"create_private_table|2"
    ),
    InlineKeyboardButton(
        text = "3",
        callback_data = f"create_private_table|3"
    ),
    InlineKeyboardButton(
        text = "4",
        callback_data = f"create_private_table|4"
    ),
    InlineKeyboardButton(
        text = "5",
        callback_data = f"create_private_table|5"
    ),
    InlineKeyboardButton(
        text = "6",
        callback_data = f"create_private_table|6"
    )
).add(
    InlineKeyboardButton(
        text = "Отмена", 
        callback_data = f"abolition"
    )
)




value_plaears_public_markup = InlineKeyboardMarkup().add(
    InlineKeyboardButton(
        text = "2",
        callback_data = f"create_public_table|2"
    ),
    InlineKeyboardButton(
        text = "3",
        callback_data = f"create_public_table|3"
    ),
    InlineKeyboardButton(
        text = "4",
        callback_data = f"create_public_table|4"
    ),
    InlineKeyboardButton(
        text = "5",
        callback_data = f"create_public_table|5"
    ),
    InlineKeyboardButton(
        text = "6",
        callback_data = f"create_public_table|6"
    )
).add(
    InlineKeyboardButton(
        text = "Отмена", 
        callback_data = f"abolition"
    )
)


create_private_table_markup = InlineKeyboardMarkup().add(
    InlineKeyboardButton(
        text = "Отменить игру", 
        callback_data = f"cancel_the_game|0"
    )
)


create_public_table_markup = InlineKeyboardMarkup().add(
    InlineKeyboardButton(
        text = "Старт",
        callback_data = f"create_public_table|"
    )
)