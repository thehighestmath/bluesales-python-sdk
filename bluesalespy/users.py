from .request import RequestApi
from .methods import UsersMethods


class Users:
    def __init__(self, request_api: RequestApi):
        self.request_api = request_api

    def get(self):
        return self.request_api.send(UsersMethods.get)
