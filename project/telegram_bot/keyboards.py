from telebot import types


def get_location_btn():
    keyboard = types.ReplyKeyboardMarkup(
        row_width=1,
        resize_keyboard=True
    )
    button_geo = types.KeyboardButton(
        text="Отправить местоположение",
        request_location=True
    )
    return keyboard.add(button_geo)
