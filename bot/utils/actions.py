import datetime as dt

from pvpc_bot.ree.price_analyzer import PriceAnalyzer
from pvpc_bot.bot.user_settings import SettingsManager
from pvpc_bot.bot.utils.logs import log
from pvpc_bot.bot.utils.images import get_image_title
from pvpc_bot.bot.utils.sections import get_color_info, get_section
from pvpc_bot.config import ROUND_DECIMALS, LOW_PERCENTILE, HIGH_PERCENTILE


def send_report_message(bot: 'telebot.TeleBot', user_id: int, target_day: 'dt.datetime', sorted_data: bool=False, pin_message: bool=False, settings_manager: 'SettingsManager'=None) -> None:
    settings_manager = settings_manager or SettingsManager()

    log(text=f"Sending report message to {user_id} for day {target_day}.", level="INFO")

    user_settings = settings_manager.users[user_id]
    pa = PriceAnalyzer(target_day, geolocation=user_settings["timezone"])
    data_summary = pa.get_summary()

    user_colors = "sections" if user_settings["colors"] == "tramos" else user_settings["colors"]
    data_list = data_summary["data"][user_colors]["list"]
    if sorted_data:
        data_list = sorted(data_list, key=lambda x: x["price"])
    
    report = f"ℹ Colores según {user_settings['colors']}.\n"
    if sorted_data:
        report += f"ℹ Precios ordenados de menor a mayor.\n"
    
    report += f"\n<b><u>{get_image_title(target_day)}</u></b>\n"
    
    # Some statistics
    report += "<pre>"
    for text, data_index in [('🔼 Precio máximo', 'max'), ('🔽 Precio mínimo', 'min')]:
        report += f"{text} ({data_summary[data_index]['datetime'].strftime('%H')}h): {round(data_summary[data_index]['price'], ROUND_DECIMALS):<{ROUND_DECIMALS + 2}} €/kWh\n"
    report += "</pre>\n<pre>"

    for text, data_index in [('📊 Media del día', 'mean'), (f'📈 Percentil {LOW_PERCENTILE}%', 'low_percentile'), (f'📉 Percentil {HIGH_PERCENTILE}%', 'high_percentile')]:
        report += f"{text}: {round(data_summary[data_index], ROUND_DECIMALS):<{ROUND_DECIMALS + 2}} €/kWh\n"
    report += "</pre>\n<pre>"

    for text, data_index in [('🟢 Media Valle', 'low'), ('🟠 Media Llano', 'mid'), ('🔴 Media Punta', 'high')]:
        if data_summary['data']['sections'][data_index]['mean'] > 0:
            report += f"{text}: {round(data_summary['data']['sections'][data_index]['mean'], ROUND_DECIMALS):<{ROUND_DECIMALS + 2}} €/kWh\n"
    
    # The real price list
    report += "</pre>"
    
    prices = "<pre>"
    for price in data_list:
        color_emoji, color_section, _ = get_color_info(price["section"])
        if user_settings['colors'] == "percentiles":
            color_emoji, _, _ = get_color_info(price["percentile_section"])
        time_start = price["datetime"].strftime("%Hh")
        time_end = (price["datetime"] + dt.timedelta(hours=1)).strftime("%Hh")
        formated_price = round(price['price'], ROUND_DECIMALS)
        
        prices += f"{color_emoji}{color_section if user_settings['colors'] == 'percentiles' else ''}\t{time_start} - {time_end}:\t{formated_price:<{ROUND_DECIMALS + 2}} €/kWh\n"

    prices +="</pre>"
    
    # The graph
    image_path = pa.generate_png(colors=user_colors)
    with open(image_path, "rb") as f:
        to_pin = bot.send_photo(user_id, f, caption=report)
    bot.send_message(user_id, prices)

    if pin_message:
        bot.pin_chat_message(user_id, to_pin.id)


def send_best_lapse(bot: 'telebot.TeleBot', user_id: int, target_day: 'dt.datetime', lapse: int, settings_manager: 'SettingsManager'=None) -> None:
    settings_manager = settings_manager or SettingsManager()
    pa = PriceAnalyzer(target_day, geolocation=settings_manager.users[user_id]["timezone"])
    summary = pa.get_summary()

    report = f"<b><u>{get_image_title(target_day)}: Análisis estadístico.</u></b>\n\n"
    report += f"ℹ Colores según percentiles.\nℹ Búsqueda de lapsos de tiempo de {lapse} horas, ordenadas de menor a mayor precio.\n\n"

    for lapse_group in find_best_lapse(lapse, pa.data):
        group_mean = lapse_group["sum"] / lapse
        color, _, _ = get_color_info(get_section(group_mean, summary["low_percentile"], summary["high_percentile"]))

        report += f"<pre>{color} [{lapse_group['start']}h - {lapse_group['end']}h]:\nPrecio total: {round(lapse_group['sum'], ROUND_DECIMALS):<{ROUND_DECIMALS + 2}} €/kW ({lapse}h)\nPrecio medio: {round(group_mean, ROUND_DECIMALS):<{ROUND_DECIMALS + 2}} €/kWh\n\n</pre>"
    bot.send_message(user_id, report)


def find_best_lapse(lapse: int, price_data: dict) -> list:
    def leading_zero(n: int) -> str:
        if n % 10 == n:
            return f"0{n}"
        return str(n)
    return sorted(
        [
            {"start": leading_zero(i), "end": leading_zero((i+lapse)%24), "sum": sum(map(lambda x: x["price"], tmp))}
            for i in range(len(price_data))
            if len(tmp := price_data[i:i+lapse]) == lapse
        ],
        key=lambda x: x["sum"]
    )
