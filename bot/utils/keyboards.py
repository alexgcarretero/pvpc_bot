from telebot import types

def get_settings_keyboards():
    return {
        "settings": settings_keyboard(),
        "subscription": settings_keyboard(),
        "regions": regions_keyboard(),
        "colors": colors_keyboard()
    }


def regions_keyboard():
    return types.InlineKeyboardMarkup(
        keyboard=[
            [
                types.InlineKeyboardButton(
                    text="📍 Península",
                    callback_data="regions:Península"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="📍 Baleares",
                    callback_data="regions:Baleares"
                ),
                types.InlineKeyboardButton(
                    text="📍 Canarias",
                    callback_data="regions:Canarias"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="📍 Ceuta",
                    callback_data="regions:Ceuta"
                ),
                types.InlineKeyboardButton(
                    text="📍 Melilla",
                    callback_data="regions:Melilla"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="↩ Atras",
                    callback_data="keyboard:settings"
                )
            ]
        ]
    )


def colors_keyboard():
    return types.InlineKeyboardMarkup(
        keyboard=[
            [
                types.InlineKeyboardButton(
                    text="📈 Percentiles",
                    callback_data="colors:percentiles"
                ),
                types.InlineKeyboardButton(
                    text="⌛ Tramos reales",
                    callback_data="colors:tramos"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="↩ Atras",
                    callback_data="keyboard:settings"
                )
            ]
        ]
    )


def settings_keyboard():
    return types.InlineKeyboardMarkup(
        keyboard=[
            [
                types.InlineKeyboardButton(
                    text=f"📰 Cambiar subscripción",
                    callback_data="keyboard:subscription"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="🗺 Cambiar Región",
                    callback_data="keyboard:regions"
                ),
                types.InlineKeyboardButton(
                    text="📊 Cambiar colores",
                    callback_data="keyboard:colors"
                )
            ]
        ]
    )
