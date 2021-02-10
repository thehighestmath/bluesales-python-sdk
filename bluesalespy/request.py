# -*- coding: utf-8 -*-
import json
import time

import requests

from .exceptions import HttpError, WrongLoginOrPassword


class RequestApi:
    __base_url = 'https://bluesales.ru/app/Customers/WebServer.aspx'

    def __init__(self, login: str, password_hash):
        self.__login = login
        self.__password = password_hash

    @property
    def login(self):
        return self.__login

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
        response = json.loads(result.text)
        if 'isValid' in response and not response['isValid']:
            if 'error' in response:
                if response['error'] == 'Неправильный логин или пароль.':
                    raise WrongLoginOrPassword(response['error'])
                if 'Другой пользователь находится онлайн под логином' in response['error']:
                    error: str = response['error']
                    p1 = "<span class='countdown'>"
                    i1 = error.index(p1)
                    p2 = "</span>"
                    i2 = error.index(p2)
                    delay = int(error[i1 + len(p1):i2])
                    print(f'Другой пользователь находится онлайн. Засыпаю на {delay + 1}')
                    time.sleep(delay + 1)
                    return self.send(method, data)
            raise Exception(response)
        return response
