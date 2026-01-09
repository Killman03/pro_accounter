from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/start")],
        [KeyboardButton(text="/profit")],
        [KeyboardButton(text="/delete_machine"), KeyboardButton(text="/delete_payment")],
    ],
    resize_keyboard=True,
    one_time_keyboard=False
) 