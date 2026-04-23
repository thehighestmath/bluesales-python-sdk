# -*- coding: utf-8 -*-
import json
import time

import requests

from bluesalespy.exceptions import BlueSalesError, HttpError, WrongLoginOrPassword


class RequestApi:
    __base_url = 'https://bluesales.ru/app/Customers/WebServer.aspx'

    def __init__(self, login: str, password_hash: str) -> None:
        self.__login = login
        self.__password = password_hash

    @property
    def login(self) -> str:
        return self.__login

    def send(self, method: str, data: dict | list | None = None) -> dict | list:
        """Отправить запрос к API.

        Args:
            method: название метода BlueSales API.
            data: тело запроса.

        Returns:
            Ответ API (dict или list).

        Raises:
            HttpError: при сетевой ошибке.
            WrongLoginOrPassword: при неверных учётных данных.
            BlueSalesError: при прочих ошибках API.
        """
        payload = {
            'login': self.__login,
            'password': self.__password,
            'command': method,
        }
        try:
            result = requests.post(url=self.__base_url, params=payload, data=json.dumps(data))
        except (ConnectionError, TimeoutError, requests.exceptions.ReadTimeout) as exc:
            raise HttpError('Ошибка подключения к API bluesales.ru') from exc

        if result.status_code == 404:
            raise HttpError(f'Метод {method!r} не найден (404)')

        response = result.json()

        if isinstance(response, dict) and 'isValid' in response and not response['isValid']:
            error_msg = response.get('error', '')
            if error_msg == 'Неправильный логин или пароль.':
                raise WrongLoginOrPassword(error_msg)
            if 'Другой пользователь находится онлайн под логином' in error_msg:
                p1 = "<span class='countdown'>"
                p2 = '</span>'
                delay = int(error_msg[error_msg.index(p1) + len(p1):error_msg.index(p2)])
                time.sleep(delay + 1)
                return self.send(method, data)
            raise BlueSalesError(f'{self.__login} | {response}')

        return response
