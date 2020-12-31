# -*- coding: utf-8 -*-
from bluesalespy.request import RequestApi


class OrdersAPI:
    def __init__(self, request_api: RequestApi):
        self.request_api = request_api
