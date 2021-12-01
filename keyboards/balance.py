from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types.reply_keyboard import ReplyKeyboardMarkup



# get_balance_markup = InlineKeyboardMarkup().add(
#     InlineKeyboardButton(
#         text = "Денежный баланс(пока не работает)",
#         callback_data = f"returneBalance|Cash"
#     ),
#     InlineKeyboardButton(
#         text = "Баланс фишек", 
#         callback_data = f"returneBalance|Chips"
#     )
# ).add(
#     InlineKeyboardButton(
#         text = "Вернуться назад", 
#         callback_data = f"back_main_menu"
#     )
# )

get_balance_markup = ReplyKeyboardMarkup(resize_keyboard=True).add("Денежный баланс", "Баланс фишек").add("Вернуться назад")


# returne_balance_chips_markup = InlineKeyboardMarkup().add(
#     InlineKeyboardButton(
#         text = "Купить Фишки",
#         callback_data = f"buyChips"
#     )
# ).add(
#     InlineKeyboardButton(
#         text = "Вернуться назад", 
#         callback_data = f"back_main_menu"
#     )
# )

returne_balance_chips_markup = ReplyKeyboardMarkup(resize_keyboard=True).add("Купить Фишки").add("Вернуться назад")


# returne_balance_cash_markup = InlineKeyboardMarkup().add(
#     InlineKeyboardButton(
#         text = "Пополнить денежный счет",
#         callback_data = f"transferMoney"
#     ),
#     InlineKeyboardButton(
#         text = "Вывести деньги со счета",
#         callback_data = f"withdrawMoney"
#     )
# ).add(
#     InlineKeyboardButton(
#         text = "Вернуться назад", 
#         callback_data = f"back_main_menu"
#     )
# )

returne_balance_cash_markup = ReplyKeyboardMarkup(resize_keyboard=True).add("Пополнить денежный счет", "Вывести деньги со счета").add("Вернуться назад")


# buy_chips_markup = InlineKeyboardMarkup().add(
#     InlineKeyboardButton(
#         text = "Карта",
#         callback_data = f"buy_chips"
#     ),
#     InlineKeyboardButton(
#         text = "QIWI",
#         callback_data = f"buy_chips"
#     ),
#     InlineKeyboardButton(
#         text = "Криптовалюта",
#         callback_data = f"buy_chips"
#     )
# ).add(
#     InlineKeyboardButton(
#         text = "Вернуться назад", 
#         callback_data = f"back_main_menu"
#     )
# )

buy_chips_markup = ReplyKeyboardMarkup(resize_keyboard=True).add("Купить фишки").add("Вернуться назад")


# transfer_money_markup = InlineKeyboardMarkup().add(
#     InlineKeyboardButton(
#         text = "Карта",
#         callback_data = f"buy_chips"
#     ),
#     InlineKeyboardButton(
#         text = "QIWI",
#         callback_data = f"buy_chips"
#     ),
#     InlineKeyboardButton(
#         text = "Криптовалюта",
#         callback_data = f"buy_chips"
#     )
# ).add(
#     InlineKeyboardButton(
#         text = "Вернуться назад", 
#         callback_data = f"back_main_menu"
#     )
# )

transfer_money_markup = ReplyKeyboardMarkup(resize_keyboard=True).add("withdraw_money_markup деньги").add("Вернуться назад")

# withdraw_money_markup = InlineKeyboardMarkup().add(
#     InlineKeyboardButton(
#         text = "Карта",
#         callback_data = f"buy_chips"
#     ),
#     InlineKeyboardButton(
#         text = "QIWI",
#         callback_data = f"buy_chips"
#     ),
#     InlineKeyboardButton(
#         text = "Криптовалюта",
#         callback_data = f"buy_chips"
#     )
# ).add(
#     InlineKeyboardButton(
#         text = "Вернуться назад", 
#         callback_data = f"back_main_menu"
#     )
# )

withdraw_money_markup = ReplyKeyboardMarkup(resize_keyboard=True).add("withdraw_money_markup деньги").add("Вернуться назад")



currency_markup = ReplyKeyboardMarkup(resize_keyboard=True).add("RUB", "KZT").add("Вернуться назад")


payout_markup = ReplyKeyboardMarkup(resize_keyboard=True).add("VISA", "MasterCard").add("Вернуться назад")

correctly_markup = ReplyKeyboardMarkup(resize_keyboard=True).add("Да", "Нет").add("Вернуться назад")