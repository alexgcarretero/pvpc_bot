import re
import os
import traceback
import datetime as dt
from functools import wraps

import telebot
from telebot import apihelper

from pvpc_bot.bot.user_settings import SettingsManager
from pvpc_bot.bot.utils.keyboards import get_settings_keyboards
from pvpc_bot.bot.utils.actions import send_report_message, send_best_lapse
from pvpc_bot.bot.utils.logs import log
from pvpc_bot.config import (
    ADMINS, ADMIN_ENABLED, ADMIN_COMMANDS, BOT_TOKEN,
    WELCOME_STICKER, WELCOME_MESSAGE, HELP_MESSAGE,
    TMP_DIR, LOGS_DIR, LOG_FILE_NAME, LOG_ERROR_FILE_NAME
)


def settings_phrases(user_settings: dict):
    is_subscribed = ""
    is_subscribed_emoji = "🔊"
    if not user_settings["subscribed"]:
        is_subscribed = "NO "
        is_subscribed_emoji = "🔇"
    settings_text = f"<b>⚙ Ajustes:\n\n{is_subscribed_emoji} Actualmente {is_subscribed}estás suscrito al bot.</b>"
    return {
        "settings": settings_text,
        "subscription": settings_text,
        "regions": f"<b> 🗺 Región actual: {user_settings['timezone']}</b>",
        "colors": f"<b>📊 Colores actuales: según {user_settings['colors']}</b>"
    }


def parse_message(message: str) -> dict:
    regex = r"/(\w+)(\s+\d+/\d+/\d+)?(\s+\d+)?"
    match = re.match(regex, message.text)
    command, day, lapse = map(lambda x: x.strip() if x is not None else x, match.groups())

    parsed_message =  {"command": command}
    if lapse is not None:
        parsed_message["lapse"] = int(lapse)

    if day is not None:
        parsed_message["day"] = dt.datetime.strptime(day, "%d/%m/%Y")
    else:
        now = dt.datetime.now()
        parsed_message["day"] = dt.datetime(now.year, now.month, now.day)  
    return parsed_message


def ReeBot(settings_manager: 'bot.user_settings.SettingsManager'=None):
    settings_manager = settings_manager or SettingsManager()
    apihelper.ENABLE_MIDDLEWARE = True
    _bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

    """def safe_execution(function):
        def wrapper(obj):
            try:
                log(obj=obj, level="DEBUG")
                function(obj)
            except Exception as e:
                log(text=traceback.format_exc(), message=obj, level="ERROR")
                message = obj.message if isinstance(obj, telebot.types.CallbackQuery) else obj
                _bot.send_message(message.chat.id, "Datos no disponibles, inténtalo mas tarde.")
        return wrapper"""
    
    def log_message(_func=None, *, reply_message=""):
        def decorator(function):
            @wraps(function)
            def wrapper(obj):
                try:
                    log(obj=obj)
                    function(obj)
                except Exception as e:
                    log(text=traceback.format_exc(), obj=obj, level="ERROR")

                    if reply_message and isinstance(obj, telebot.types.Message):
                        _bot.reply_to(obj, reply_message)
            return wrapper
        return decorator if _func is None else decorator(_func)

    @_bot.message_handler(commands=['ayuda'])
    @log_message
    def ayuda(message):
        _bot.reply_to(message, HELP_MESSAGE)

    @_bot.message_handler(commands=['start'])
    @log_message
    def send_welcome(message):
        _bot.reply_to(message, WELCOME_MESSAGE)
        _bot.send_sticker(message.chat.id, WELCOME_STICKER) 
        settings_manager.register_user(message.chat.id)
    
    @_bot.message_handler(commands=['precios'])
    @log_message(reply_message="Datos no disponibles, inténtalo mas tarde.")
    def precios(message):
        command_data = parse_message(message)
        send_report_message(_bot, user_id=message.chat.id, target_day=command_data["day"], settings_manager=settings_manager)

    @_bot.message_handler(commands=['siguientes'])
    @log_message(reply_message="Datos no disponibles, inténtalo mas tarde.")
    def siguientes(message):
        command_data = parse_message(message)
        send_report_message(_bot, user_id=message.chat.id, target_day=command_data["day"]+dt.timedelta(days=1), settings_manager=settings_manager)

    @_bot.message_handler(commands=['analisis'])
    @log_message(reply_message="Datos no disponibles, inténtalo mas tarde.")
    def analisis(message):
        command_data = parse_message(message)
        if "lapse" in command_data:
            send_best_lapse(_bot, user_id=message.chat.id, target_day=command_data["day"], lapse=command_data["lapse"], settings_manager=settings_manager)
        else:
            send_report_message(_bot, user_id=message.chat.id, target_day=command_data["day"], sorted_data=True, settings_manager=settings_manager)
    
    @_bot.message_handler(commands=["ajustes"])
    @log_message
    def settings(message):
        user_id = message.chat.id
        _bot.send_message(user_id, settings_phrases(settings_manager.users[user_id])["settings"], reply_markup=get_settings_keyboards()["settings"])
    
    @_bot.callback_query_handler(func=lambda call: True)
    @log_message
    def settings_handler(call):
        message = call.message
        user_id = message.chat.id
        action, data = call.data.split(":")

        keyboards = get_settings_keyboards()
        
        action_index = data if action == "keyboard" else action
        callback_message_response = ""
        keyboard = keyboards[action_index]
        
        if action == "regions":
            settings_manager.set_config(user_id, "timezone", data)
            callback_message_response = f'Cambiada la región a {data}'
        elif action == "colors":
            settings_manager.set_config(user_id, "colors", data)
            callback_message_response = f'Cambiado el color a {data}'
        elif data == "subscription":
            is_subscribed = settings_manager.users[user_id]["subscribed"]
            settings_manager.set_config(user_id, "subscribed", not is_subscribed)
            callback_message_response = 'Subscripción actualizada.'
        
        # Callback response and action taken
        phrases = settings_phrases(settings_manager.users[user_id])
        _bot.answer_callback_query(callback_query_id=call.id, text=callback_message_response)
        _bot.edit_message_text(phrases[action_index], user_id, message.id, reply_markup=keyboard)
    
    if ADMIN_ENABLED:
        admin_functions(_bot=_bot, settings_manager=settings_manager)
    return _bot


def admin_functions(_bot: 'telebot.TeleBot', settings_manager: 'bot.user_settings.SettingsManager'=None):
    settings_manager = settings_manager or SettingsManager()

    def is_admin(user_id: int) -> bool:
        user_settings = settings_manager.users[user_id]
        return "admin" in user_settings and user_settings["admin"]
    
    def set_admins():
        for admin in ADMINS:
            if not is_admin(admin):
                settings_manager.set_config(admin, "admin", True)
    
    def get_all_admins():
        return [user for user in settings_manager.users if settings_manager.users[user]["admin"]]
    
    def get_logs(message, log_type):
        def join_logs(final_log_file_path):
            full_log_text = ""
            for log_file in os.listdir(LOGS_DIR):
                regex = re.compile(f"bot_{log_type}(.\d+-\d+-\d+)?.log")
                match = re.match(regex, log_file)
                if match:
                    with open(os.path.join(LOGS_DIR, log_file), "rt") as f:
                        full_log_text += f.read()

            with open(final_log_file_path, "wt") as f:
                f.write(full_log_text)
        
        base_filename = LOG_ERROR_FILE_NAME if log_type == "errors" else LOG_FILE_NAME
        message_text = message.text.split()
        log_file_path = os.path.join(LOGS_DIR, base_filename)
        if len(message_text) > 1:
            if message_text[1].lower() == "all":
                log_file_path = os.path.join(TMP_DIR, f"tmp_{log_type}_{message.chat.id}.log")
                join_logs(log_file_path)
            else:
                date = dt.datetime.strptime("%d/%m/%Y")
                log_file_path = os.path.join(LOGS_DIR, f"{base_filename.replace('.log', '')}.{date.strftime('%Y-%m-%d')}.log")
        
        with open(log_file_path, "rb") as f:
            _bot.send_document(message.chat.id, f)
        
        if message_text[1].lower() == "all":
            os.remove(log_file_path)
    
    def check_admin(function):
        def wrapper(message):
            command, *_ = message.text.split()
            if command in ADMIN_COMMANDS and not is_admin(message.chat.id):
                log(text=f"USER not ALLOWED TO EXECUTE ADMIN COMMAND '{command}'", message=message)
            else:
                log(text=f"USER ALLOWED TO EXECUTE COMMAND '{command}'", message=message)
                function(message)
        return wrapper
        
    set_admins()

    @_bot.message_handler(commands=['users'])
    @check_admin
    def users(message):
        backup_path = os.path.join(TMP_DIR, f"tmp_backup_{message.chat.id}.json")
        if not os.path.exists(backup_path):
            settings_manager.backup_settings(system=True, backup_path=backup_path)
        
        with open(backup_path, "rb") as f:
            _bot.send_document(message.chat.id, f)
        os.remove(backup_path)
    
    @_bot.message_handler(commands=['op'])
    @check_admin
    def op(message):
        try:
            user_id = int(message.text.split()[1])
            settings_manager.set_config(user_id, "admin", True)
            _bot.send_message(message.chat.id, f"OPed user {user_id}.")
            _bot.send_message(message.chat.id, f"Ahora mismo los ADMINS son: {get_all_admins()}")
        except (ValueError, IndexError):
            _bot.send_message(message.chat.id, f"Algo ha salido mal, inténtalo de nuevo.")
    
    @_bot.message_handler(commands=['deop'])
    @check_admin
    def deop(message):
        try:
            user_id = int(message.text.split()[1])
            settings_manager.set_config(user_id, "admin", False)
            _bot.send_message(message.chat.id, f"DEOPed user {user_id}.")
            _bot.send_message(message.chat.id, f"Ahora mismo los ADMINS son: {get_all_admins()}")
        except (ValueError, IndexError):
            _bot.send_message(message.chat.id, f"Algo ha salido mal, inténtalo de nuevo.")

    @_bot.message_handler(commands=['logs'])
    @check_admin
    def logs(message):
        get_logs(message, "logs")

    @_bot.message_handler(commands=['errors'])
    @check_admin
    def errors(message):
        get_logs(message, "errors")
