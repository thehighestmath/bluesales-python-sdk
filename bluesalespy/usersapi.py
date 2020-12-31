# -*- coding: utf-8 -*-
from .request import RequestApi
from .methods import UsersMethods


class UsersAPI:
    def __init__(self, request_api: RequestApi):
        self.request_api = request_api

    def get(self):
        return self.request_api.send(method=UsersMethods.get)
