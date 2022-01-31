from telebot.types import Message, CallbackQuery
import logging
import logging.config

from pvpc_bot.config import LOGGING_CONFIG


def _get_username(obj: 'Any[telebot.types.Message, telebot.types.CallbackQuery]') -> str:
    message = obj.message if isinstance(obj, CallbackQuery) else obj
    if hasattr(message.chat, "username"):
        return message.chat.username
    return ""


def _get_user_id(obj: 'Any[telebot.types.Message, telebot.types.CallbackQuery]') -> int:
    message = obj.message if isinstance(obj, CallbackQuery) else obj
    return message.chat.id


def _get_info(obj: 'Any[telebot.types.Message, telebot.types.CallbackQuery]') -> 'tuple[str]':
    if isinstance(obj, CallbackQuery):
        return "QUERY", obj.data

    command, *_ = obj.text.split()
    if not command.startswith('/'):
        command = ""
    return "COMMAND", command


def _get_logger() -> 'logging.Logger':
    logging.config.dictConfig(LOGGING_CONFIG)
    bot_logger = logging.getLogger('bot_base_logger')
    namer = lambda n: f"{n.replace('.log', '')}.log"
    for handler in bot_logger.handlers:
        handler.namer = namer
    return bot_logger


bot_logger = _get_logger()
def log(text: str="", obj: 'Any[telebot.types.Message, telebot.types.CallbackQuery]'=None, level: str="DEBUG"):
    log_text = ""
    if obj is not None:
        user_id = _get_user_id(obj)
        username = _get_username(obj)
        message_type, message_data = _get_info(obj)
        log_text += f"[ID: {user_id}] [USERNAME: {username}] [{message_type}: {message_data}]"
    
    if text:
        log_text += f"\n{text}"
    
    if obj is not None:
        log_text += f"\n{obj}"

    bot_logger.log(level=getattr(logging, level), msg=log_text)
