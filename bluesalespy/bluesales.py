# -*- coding: utf-8 -*-
import hashlib
import logging

from .customersapi import CustomersAPI
from .ordersapi import OrdersAPI
from .request import RequestApi
from .usersapi import UsersAPI

logger = logging.getLogger(__name__)


def get_hash(password):
    return hashlib.md5(bytearray(password, 'utf-8')).hexdigest().upper()


class BlueSales:
    def __init__(self, login: str, password: str):
        self.login: str = login
        self.__password: str = get_hash(password)
        self._rq = RequestApi(self.login, self.__password)
        self.customers: CustomersAPI = CustomersAPI(self._rq)
        self.orders: OrdersAPI = OrdersAPI(self._rq)
        self.users: UsersAPI = UsersAPI(self._rq)
