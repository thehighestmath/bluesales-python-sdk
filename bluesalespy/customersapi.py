# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from typing import List

from progress.bar import Bar as Bar

from .exceptions import TooLargeBoarders
from .methods import CustomersMethods
from .request import RequestApi

MAX_COUNT_CUSTOMERS_PER_REQUEST = 500


class CustomersAPI:
    def __init__(self, request_api: RequestApi):
        self.request_api = request_api

    def get(
            self,
            first_contact_date_from: datetime = None,
            first_contact_date_to: datetime = None,
            next_contact_date_from: datetime = None,
            next_contact_date_to: datetime = None,
            last_contact_date_from: datetime = None,
            last_contact_date_to: datetime = None,
            ids: List[int] = None,
            vk_ids: List[int] = None,
            count: int = 500,
            offset: int = 0,
            tags: List[str] = None,
            managers: list = None,
            sources=None,
            phone=None
    ):
        if tags is None:
            tags = []
        if managers is None:
            managers = []
        if count > MAX_COUNT_CUSTOMERS_PER_REQUEST:
            raise TooLargeBoarders(
                f'Количество запрашиваемых клиентов за раз должно быть меньше {MAX_COUNT_CUSTOMERS_PER_REQUEST}'
            )
        tags = [{'name': name} for name in tags]
        managers_out = []
        for manager in managers:
            if isinstance(manager, int):
                managers_out.append({'id': manager})
            elif isinstance(manager, str):
                managers_out.append({'login': manager})
            else:
                raise TypeError(f'Ожидалось int или str, получил {type(manager)}')
        data = {
            'firstContactDateFrom': first_contact_date_from.strftime('%Y-%m-%d') if first_contact_date_from else None,
            'firstContactDateTill': (first_contact_date_to + timedelta(days=1)).strftime(
                '%Y-%m-%d') if first_contact_date_to else None,
            'nextContactDateFrom': next_contact_date_from.strftime('%Y-%m-%d') if next_contact_date_from else None,
            'nextContactDateTill': (next_contact_date_to + timedelta(days=1)).strftime(
                '%Y-%m-%d') if next_contact_date_to else None,
            'lastContactDateFrom': last_contact_date_from.strftime('%Y-%m-%d') if last_contact_date_from else None,
            'lastContactDateTill': (last_contact_date_to + timedelta(days=1)).strftime(
                '%Y-%m-%d') if last_contact_date_to else None,
            'ids': ids,
            'vkIds': vk_ids,
            'pageSize': count,
            'startRowNumber': offset,
            'tags': tags,
            'managers': managers_out,
            'sources': sources,
            'phone': phone,
        }
        response = self.request_api.send(
            CustomersMethods.get,
            data=data
        )

        return CustomersResponse(response)

    def get_all(
            self,
            first_contact_date_from: datetime = None,
            first_contact_date_to: datetime = None,
            next_contact_date_from: datetime = None,
            next_contact_date_to: datetime = None,
            last_contact_date_from: datetime = None,
            last_contact_date_to: datetime = None,
            ids: List[int] = None,
            vk_ids: List[int] = None,
            tags: List[str] = None,
            managers: list = None,
            sources=None,
            phone=None
    ) -> List[dict]:

        items = []
        count = MAX_COUNT_CUSTOMERS_PER_REQUEST
        offset = 0

        r = self.get(
            first_contact_date_from, first_contact_date_to,
            next_contact_date_from, next_contact_date_to,
            last_contact_date_from, last_contact_date_to,
            ids, vk_ids, count=1, offset=0,
            tags=tags, managers=managers, sources=sources, phone=phone
        )
        total_count = r.not_returned_count + r.count
        
        if total_count == 0:
            return [] 
        
        with Bar(f'Получение всех клиентов из {self.request_api.login} аккаунта',
                 max=total_count, fill='█', empty_fill='░') as bar:
            while len(items) < total_count:
                r = self.get(
                    first_contact_date_from, first_contact_date_to,
                    next_contact_date_from, next_contact_date_to,
                    last_contact_date_from, last_contact_date_to,
                    ids, vk_ids, count, offset,
                    tags, managers, sources, phone
                )
                items.extend(r.customers)
                offset += count
                bar.next(r.count)
        return items


class CustomersResponse:
    def __init__(self, response: dict):
        self.count: int = response['count']
        self.not_returned_count: int = response['notReturnedCount']
        self.customers: list = response['customers']
        self.response: dict = response

    def __repr__(self):
        return str(self.response)
