# -*- coding: utf-8 -*-
import hashlib
import logging

from .customers import Customers
from .orders import Orders
from .request import RequestApi
from .users import Users

logger = logging.getLogger(__name__)


def get_hash(password):
    return hashlib.md5(bytearray(password, 'utf-8')).hexdigest().upper()


class BlueSales:

    def __init__(self, login: str, password: str):
        self.login: str = login
        self.__password: str = get_hash(password)
        self._rq = RequestApi(self.login, self.__password)
        self.customers: Customers = Customers(self._rq)
        self.orders: Orders = Orders(self._rq)
        self.users: Users = Users(self._rq)

    # def __call__(self, method, **kwargs):
    #     if 'vk_group_id' not in kwargs.keys():
    #         if self.vk_group is None:
    #             raise WrongId('vk_group_id is not specified by any of the methods')
    #         kwargs['vk_group_id'] = self.vk_group
    #     response = self._rq.send(str(method), kwargs)
    #     json_response = {}
    #     try:
    #         json_response = json.loads(response.text)
    #     except:
    #         logger.debug(f'{response.status_code}:{response.text}')
    #         raise HttpError(f'status_code:{response.status_code}, error with decode json')
    #     return self.__error_handler(json_response)
    #
    # def __error_handler(self, response):
    #     if bool(response['success']):
    #         return response
    #     raise ApiError(response)
    #
    #
    # @property
    # def secret(self):
    #     return self.__secret
    #
    # @property
    # def vk_group(self):
    #     return self.__vk_group
    #
    # @vk_group.setter
    # def vk_group(self, value):
    #     self.__vk_group = str(value)
