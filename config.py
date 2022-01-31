import os


# Storage Path Config
HOME = "."
DATA_DIR = os.path.join(HOME, "data")
CACHE_DIR = os.path.join(DATA_DIR, "cache")
IMAGE_DIR = os.path.join(CACHE_DIR, "graphs")
SETTINGS_DIR = os.path.join(DATA_DIR, "settings")
LOGS_DIR = os.path.join(DATA_DIR, "logs")
TMP_DIR = os.path.join(DATA_DIR, "tmp")
TASKS_PATH = os.path.join(HOME, "tasks")
TASKS_FILE = os.path.join(TASKS_PATH, "tasks.yaml")


# API Config
API_TOKEN = ""
BASE_API = "https://api.esios.ree.es"
PRICES_URL = f"{BASE_API}/indicators/1001"
SECTIONS_URL = f"{BASE_API}/indicators/1002"
API_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
DEFAULT_GEOLOCATION = "Península"


# Data Config
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"
LOW_PERCENTILE = 25
HIGH_PERCENTILE = 70
ROUND_DECIMALS = 5
SECTION_DATA = [("high", 1), ("mid", 2), ("low", 3)]

# Data Config: Image Config
IMAGE_NAME_DATETIME_FORMAT = "%Y%m%d.png"
IMAGE_TITLE_DATETIME_FORMAT = "%A %-d of %B of %Y"
IMAGE_X_LABEL = 'Tiempo (horas)'
IMAGE_Y_LABEL = 'Precio (€/kWh)'

# Bot Config
BOT_TOKEN = ""
ADMIN_ENABLED = True
ADMIN_COMMANDS = {"/users", "/logs", "/errors", "/op", "/deop"}
ADMINS = {}
USERNAME_BOT = "@"
WELCOME_STICKER = "CAACAgIAAxkBAAIZtmG7xqAThaURsQfRbA2WBsheCoBKAAJaDwACwWSJS2gGfUBK_uGIIwQ"
WELCOME_MESSAGE = f"""
    👋 Bienvenido a {USERNAME_BOT} !!
    
    Aquí encontraras todos los días los precios de la luz desglosados por horas, tramos horarios; con gráficas y análisis estadísticos básicos.
        
    💡 También podrás pedir que te calcule los tramos de varias horas seguidas que son más baratos, por si quieres conectar algún dispositivo en concreto y quieres saber en qué hora sale bas rentable 💰.
        
    ❓ Para saber más sobre los comandos puedes hacer <b><i>/ayuda</i></b>
    """
HELP_MESSAGE = """
    <u><b>💻 Lista de comandos:</b></u>

    ⚙ <i>/ajustes</i>
        Para cambiar los ajustes (localización, colores de las gráficas, apagar las notificaciones diarias...)

    ❓ <i>/ayuda</i>
        Muestra este menú de ayuda

    📊 <i>/precios</i>
        Muestra los precios del día desglosados por horas, junto con una gráfica y un breve resumen estadístico.
        
        ℹ Si quieres ver los precios de un día específico puedes poner <i>/precios DD/MM/AAAA</i>

    📊 <i>/siguientes</i>
        Muestra los precios del día siguiente desglosados por horas, junto con una gráfica y un breve resumen estadístico.
        
    📊 <i>/analisis</i>
        Te devuelve la lista de precios del día ordenados de más barato a más caro

        ℹ Si quieres ver la lista de precios del día ordenados de un día específico puedes poner <i>/analisis DD/MM/AAAA</i>

        ℹ Si quieres calcular los tramos de X horas seguidas que son más baratos a lo largo del día puedes poner <i>/analisis X</i>

        ℹ Puedes combinar ambas opciones y poner <i>/analisis X DD/MM/AAAA</i> o <i>/analisis DD/MM/AAAA X</i> para saber los conjuntos de X horas más baratas del dia seleccionado.
    """

LOG_FILE_NAME = "bot_logs.log"
LOG_ERROR_FILE_NAME = "bot_errors.log"
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'formatter': {
            'format': '[%(asctime)s] [%(levelname)s] %(message)s\n\n'
        },
    },
    'handlers': {
        'std_handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, LOG_FILE_NAME),
            'when': 'midnight',
            'formatter': 'formatter',
        },
        'err_handler': {
            'level': 'WARNING',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, LOG_ERROR_FILE_NAME),
            'when': 'midnight',
            'formatter': 'formatter',
        },
    },
    'loggers': {
        'bot_base_logger': {
            'handlers': ['std_handler', 'err_handler'],
            'propagate': True,
            'level': 'DEBUG',
        },
    }
}
