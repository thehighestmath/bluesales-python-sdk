# -*- coding: utf-8 -*-
from .request import RequestApi
from .methods import UsersMethods


class User:
    __slots__ = (
        'full_name', 'email', 'login', 'response'
    )

    def __init__(self, user_json):
        self.full_name: str = user_json['fullName']
        self.email: str = user_json['email']
        self.login: str = user_json['login']
        self.response = user_json

    def __repr__(self):
        return str(self.response)


class UsersResponse:
    def __init__(self, response: dict):
        self.users: list = [User(user_json) for user_json in response]
        self.response: dict = response

    def __repr__(self):
        return str(self.response)


class UsersAPI:
    def __init__(self, request_api: RequestApi):
        self.request_api = request_api

    def get(self):
        response = self.request_api.send(method=UsersMethods.get)
        return UsersResponse(response).users
