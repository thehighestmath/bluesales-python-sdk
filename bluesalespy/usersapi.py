# -*- coding: utf-8 -*-
from bluesalespy.methods import UsersMethods
from bluesalespy.request import RequestApi


class UsersAPI:
    def __init__(self, request_api: RequestApi) -> None:
        self.request_api = request_api

    def get(self) -> list[dict]:
        """Получить список пользователей (менеджеров) BlueSales."""
        return self.request_api.send(method=UsersMethods.get)
