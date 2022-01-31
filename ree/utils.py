import json
import threading
import datetime as dt

from pvpc_bot.config import DATETIME_FORMAT


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, dt.datetime):
            return obj.strftime(DATETIME_FORMAT)
        return json.JSONEncoder.default(self, obj)

_store_mutex = threading.Lock()
def store_data(json_data: dict, file_path: str, wait: bool=False) -> None:
    def _store_data():
        with _store_mutex:
            with open(file_path, "wt", encoding="utf-8") as f:
                f.write(json.dumps(json_data, indent=2, ensure_ascii=False))
    if wait:
        _store_data()
    else:
        threading.Thread(target=_store_data).start()


def load_data(file_path: str) -> dict:
    with open(file_path, "rt") as f:
        return json.loads(f.read())
