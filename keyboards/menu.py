from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types.reply_keyboard import ReplyKeyboardMarkup


# mein_menu_markup = InlineKeyboardMarkup().add(
#     InlineKeyboardButton(
#         text = "Начать игру!",
#         callback_data = f"create_game"
#     ),
#     InlineKeyboardButton(
#         text = "Баланс!", 
#         callback_data = f"getBalance"
#     ),
#     InlineKeyboardButton(
#         text = "Настройки", 
#         callback_data = f"setings"
#     ),
#     InlineKeyboardButton(
#         text = "Рейтинг игроков", 
#         callback_data = f"reiting"
#     ),
#     InlineKeyboardButton(
#         text = "Выйти", 
#         callback_data = f"exitAZI"
#     ),
#     InlineKeyboardButton(
#         text = "Правила", 
#         callback_data = f"regulations"
#     )
# )



mein_menu_markup = ReplyKeyboardMarkup(resize_keyboard=True).add("Начать игру!", "Баланс!", "Друзья", "Настройки", "Правила"
)






# setings_markup = InlineKeyboardMarkup().add(
#     InlineKeyboardButton(
#         text = "Язык", 
#         callback_data = f"language"
#     ),
#     InlineKeyboardButton(
#         text = "Вернуться назад", 
#         callback_data = f"back_main_menu"
#     )
# )



setings_markup = ReplyKeyboardMarkup(resize_keyboard=True).add("Язык","Вернуться назад"
)



# language_markup = InlineKeyboardMarkup().add(
#     InlineKeyboardButton(
#         text = "Русский", 
#         callback_data = f"language"
#     ),
#     InlineKeyboardButton(
#         text = "Вернуться назад", 
#         callback_data = f"back_main_menu"
#     )
# )


language_markup = ReplyKeyboardMarkup(resize_keyboard=True).add("Русский","Вернуться назад")


# back_main_menu_markup = InlineKeyboardMarkup().add(
#     InlineKeyboardButton(
#         text = "Вернуться назад", 
#         callback_data = f"back_main_menu"
#     )
# )



back_main_menu_markup = ReplyKeyboardMarkup(resize_keyboard=True).add("Вернуться назад"
)