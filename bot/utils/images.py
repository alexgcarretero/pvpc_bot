from pvpc_bot.config import IMAGE_NAME_DATETIME_FORMAT, IMAGE_TITLE_DATETIME_FORMAT


def translate(input_string: str) -> str:
        traductor = {
            "Monday": "Lunes",
            "Tuesday": "Martes",
            "Wednesday": "Miércoles",
            "Thursday": "Jueves",
            "Friday": "Viernes",
            "Saturday": "Sábado",
            "Sunday": "Domingo",
            "January": "enero",
            "February": "febrero",
            "March": "marzo",
            "April": "abril",
            "May": "mayo",
            "June": "junio",
            "July": "julio",
            "August": "agosto",
            "September": "septiembre",
            "October": "octubre",
            "November": "noviembre",
            "December": "diciembre",
            "of": "de",
            "Low": "Valle",
            "High": "Punta",
            "Mid": "Llano"
        }
        return ' '.join([traductor.get(word, word) for word in input_string.split()])


def get_image_name(date: 'datetime.datetime') -> str:
    return date.strftime(IMAGE_NAME_DATETIME_FORMAT)


def get_image_title(date: 'datetime.datetime') -> str:
    return translate(date.strftime(IMAGE_TITLE_DATETIME_FORMAT))


def get_image_legend(section: str, colors: str) -> str:
    return f"Horas {translate(section.capitalize())}{'' if colors == 'sections' else ' según precios relativos'}"
