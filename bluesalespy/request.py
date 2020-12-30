# -*- coding: utf-8 -*-
import json

import requests

from .exceptions import HttpError


class RequestApi:
    __base_url = 'https://bluesales.ru/app/Customers/WebServer.aspx'

    def __init__(self, login: str, password_hash):
        self.__login = login
        self.__password = password_hash

    def send(self, method, data=None):
        payload = {
            'login': self.__login,
            'password': self.__password,
            'command': method
        }
        try:
            result = requests.post(url=self.__base_url, params=payload, data=json.dumps(data))
        except (ConnectionError, TimeoutError, requests.exceptions.ReadTimeout):
            raise HttpError('Error with connection to bluesales.ru API server')
        if result.status_code == 404:
            raise HttpError(f'Method {method} not found!')
        return json.loads(result.text)

