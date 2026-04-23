# -*- coding: utf-8 -*-
import hashlib
import logging

from bluesalespy.customersapi import CustomersAPI
from bluesalespy.ordersapi import OrdersAPI
from bluesalespy.request import RequestApi
from bluesalespy.tagsapi import TagsAPI
from bluesalespy.usersapi import UsersAPI

logger = logging.getLogger(__name__)


def get_hash(password: str) -> str:
    return hashlib.md5(password.encode('utf-8')).hexdigest().upper()


class BlueSales:
    """Клиент BlueSales CRM API.

    Args:
        login: логин (email) пользователя BlueSales.
        password: пароль в открытом виде (будет захеширован автоматически).

    Example::

        from bluesalespy import BlueSales

        bs = BlueSales('login@example.com', 'password')
        users = bs.users.get()
    """

    def __init__(self, login: str, password: str):
        self.login: str = login
        self._rq = RequestApi(login, get_hash(password))
        self.customers: CustomersAPI = CustomersAPI(self._rq)
        self.orders: OrdersAPI = OrdersAPI(self._rq)
        self.users: UsersAPI = UsersAPI(self._rq)
        self.tags: TagsAPI = TagsAPI(self._rq)

    def call_api(self, method: str, data=None):
        """Произвольный вызов метода BlueSales API.

        Args:
            method: название метода (например, ``'customers.get'``).
            data: тело запроса (dict или list).

        Returns:
            Ответ API (dict или list).

        Example::

            result = bs.call_api('customers.get', data={'pageSize': 10})
        """
        return self._rq.send(method, data=data)
