from telebot import types


def get_location_keyaboard():
    keyboard = types.ReplyKeyboardMarkup(
        row_width=1,
        resize_keyboard=True
    )
    button_geo = types.KeyboardButton(
        text="Отправить местоположение",
        request_location=True
    )
    return keyboard.add(button_geo)


def get_loc_and_phone_keyboard(user):
    keyboard = types.ReplyKeyboardMarkup(
        row_width=1,
        resize_keyboard=True
    )
    button_phone = types.KeyboardButton(
        text="Отправить номер телефона",
        request_contact=True
    )
    button_geo = types.KeyboardButton(
        text="Отправить местоположение",
        request_location=True
    )
    if not user.timezone:
        keyboard.add(button_geo)
    if not user.phone:
        keyboard.add(button_phone)
    return keyboard


def get_buy_keyboard():
    inlinekeyboard = types.InlineKeyboardMarkup(
        row_width=1
    )
    inlinekeyboard.add(
        types.InlineKeyboardButton(
            "Оплатить", callback_data="buy"
        )
    )

    return inlinekeyboard
