import datetime as dt

import telebot

from pvpc_bot.bot.user_settings import SettingsManager
from pvpc_bot.bot.utils.actions import send_report_message
from pvpc_bot.bot.utils.logs import log
from pvpc_bot.config import BOT_TOKEN


def daily_report():
    bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
    settings_manager = SettingsManager()

    now = dt.datetime.now()
    today = dt.datetime(now.year, now.month, now.day)
    log(text=f"Starting task sending for day: {today}")
    for user_id in settings_manager.users:
        # Get the user settings and send the proper data to them
        if settings_manager.users[user_id]["subscribed"]:
            log(text=f"Message sento to {user_id} with date: {today}")
            send_report_message(bot, user_id, today)
