import os
import json
import requests
import datetime as dt
from json.decoder import JSONDecodeError

from pvpc_bot.ree.utils import store_data
from pvpc_bot.config import API_TOKEN, PRICES_URL, SECTIONS_URL, API_DATETIME_FORMAT, CACHE_DIR


# Exceptions
class ResponseError(Exception):
    pass


class DocumentNotFound(Exception):
    pass


# API
class ReeAPI:
    def __init__(self, token=API_TOKEN):
        self.cache = ReeCache(token)
    
    def _request(self, method: str, year: int, month: int, day: int) -> dict:
        try:
            date = dt.datetime(year, month, day)
        except TypeError:
            today = dt.date.today()
            date = dt.datetime(today.year, today.month, today.day)
        return self.cache.get_data(method, date)
        
    def get_prices(self, year: int=None, month: int=None, day: int=None) -> dict:
        return self._request("prices", year, month, day)

    def get_sections(self, year: int=None, month: int=None, day: int=None) -> dict:
        return self._request("sections", year, month, day)


class ReeCache:
    def __init__(self, token):
        self.token = token

        # Request urls
        self.urls = {
            "prices": PRICES_URL,
            "sections": SECTIONS_URL
        }

        # Request headers
        self.headers = {
            "Content-Type": "application/json"
        }
        if self.token:
            self.headers["Authorization"] = f'Token token="{self.token}"'
    
    def _generate_request_params(self, start_date: 'dt.datetime') -> dict:
        params = {}
        if self.token:
            end_date = start_date + dt.timedelta(days=1, seconds=-1)
            params["start_date"] = start_date.strftime(API_DATETIME_FORMAT)
            params["end_date"] = end_date.strftime(API_DATETIME_FORMAT)
        return params

    def _generate_file_path(self, method: str, date: 'dt.datetime') -> str:
        filename = f"{method}_{date.strftime('%Y%m%d')}.json"
        return os.path.join(CACHE_DIR, filename)

    def get_document(self, method: str, date: 'dt.datetime') -> dict:
        document = self._generate_file_path(method, date)
        if os.path.exists(document):
            with open(document, "r") as f:
                return json.loads(f.read())
        raise DocumentNotFound()
    
    def put_document(self, data: dict, method: str, date: 'dt.datetime') -> None:
        store_data(data, self._generate_file_path(method, date))
    
    def request(self, method: str, start_date: 'dt.datetime') -> dict:
        response = requests.get(
            self.urls[method],
            headers=self.headers,
            params=self._generate_request_params(start_date)
        )
        response.raise_for_status()

        try:
            return response.json()
        except JSONDecodeError:
            raise ResponseError(f"Could not parse response: {response.text}")

    def get_data(self, method: str, start_date: 'dt.datetime') -> dict:
        try:
            # Check if cached
            response_data = self.get_document(method, start_date)
        except DocumentNotFound:
            # Make the request and save the result
            response_data = self.request(method, start_date)
            if response_data["indicator"]["values"]:
                self.put_document(response_data, method, start_date)
        return response_data
