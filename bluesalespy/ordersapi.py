# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from typing import List

from .exceptions import TooLargeBoarders
from .methods import OrdersMethods
from .request import RequestApi

MAX_COUNT_CUSTOMERS_PER_REQUEST = 500


class OrdersAPI:
    def __init__(self, request_api: RequestApi):
        self.request_api = request_api

    def get(
            self,
            date_from: datetime = None,
            date_to: datetime = None,
            order_statuses: list = None,
            ids: List[int] = None,
            internal_numbers: List[int] = None,
            customer_id: int = None,
            count: int = 500,
            offset: int = 0
    ):
        if order_statuses is None:
            order_statuses = []
        if count > MAX_COUNT_CUSTOMERS_PER_REQUEST:
            raise TooLargeBoarders(
                f'Количество запрашиваемых клиентов за раз должно быть меньше {MAX_COUNT_CUSTOMERS_PER_REQUEST}'
            )
        out_statuses = []
        for status in order_statuses:
            if isinstance(status, int):
                out_statuses.append({'id': status})
            elif isinstance(status, str):
                out_statuses.append({'name': status})
            else:
                raise TypeError(f'Ожидалось int или str, получил {type(status)}')

        data = {
            'dateFrom': date_from.strftime('%Y-%m-%d') if date_from else None,
            'dateTill': (date_to + timedelta(days=1)).strftime(
                '%Y-%m-%d') if date_to else None,
            'orderStatuses': out_statuses,
            'customerId': customer_id,
            'ids': ids,
            'internalNumbers': internal_numbers,
            'pageSize': count,
            'startRowNumber': offset,
        }
        response = self.request_api.send(
            OrdersMethods.get,
            data=data
        )

        return OrdersResponse(response)


class OrdersResponse:
    def __init__(self, response: dict):
        self.response: dict = response

    def __repr__(self):
        return str(self.response)
