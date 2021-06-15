# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from typing import List

import pytz
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
            phone=None,
            is_right_enabled=True
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

        if is_right_enabled:
            first_contact_date_to = first_contact_date_to + timedelta(days=1) if first_contact_date_to else None
            next_contact_date_to = next_contact_date_to + timedelta(days=1) if next_contact_date_to else None
            last_contact_date_to = last_contact_date_to + timedelta(days=1) if last_contact_date_to else None
        data = {
            'firstContactDateFrom': first_contact_date_from.strftime('%Y-%m-%d') if first_contact_date_from else None,
            'firstContactDateTill': first_contact_date_to.strftime('%Y-%m-%d') if first_contact_date_to else None,
            'nextContactDateFrom': next_contact_date_from.strftime('%Y-%m-%d') if next_contact_date_from else None,
            'nextContactDateTill': next_contact_date_to.strftime('%Y-%m-%d') if next_contact_date_to else None,
            'lastContactDateFrom': last_contact_date_from.strftime('%Y-%m-%d') if last_contact_date_from else None,
            'lastContactDateTill': last_contact_date_to.strftime('%Y-%m-%d') if last_contact_date_to else None,
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

    def get_all_with_step(
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
            phone=None,
            is_right_enabled=False,
            days_count: int = 1
    ) -> List[dict]:

        total_items = []
        count = MAX_COUNT_CUSTOMERS_PER_REQUEST
        current_first_contact_date = first_contact_date_from
        while current_first_contact_date < first_contact_date_to:
            current_first_contact_date_to = current_first_contact_date + timedelta(days=days_count)
            query = dict(
                first_contact_date_from=current_first_contact_date,
                first_contact_date_to=current_first_contact_date_to,
                next_contact_date_from=next_contact_date_from,
                next_contact_date_to=next_contact_date_to,
                last_contact_date_from=last_contact_date_from,
                last_contact_date_to=last_contact_date_to,
                ids=ids,
                vk_ids=vk_ids,
                tags=tags,
                managers=managers,
                sources=sources,
                phone=phone,
                is_right_enabled=is_right_enabled
            )
            r = self.get(**query, count=1, offset=0)

            offset = 0
            items = []
            total_count = r.not_returned_count + r.count
            if total_count == 0:
                current_first_contact_date += timedelta(days=days_count)
                continue

            with Bar(f"Customers [{current_first_contact_date.strftime('%d.%m.%Y')} - "
                     f"{current_first_contact_date_to.strftime('%d.%m.%Y')}) "
                     f"| {self.request_api.login}",
                     max=total_count, fill='█', empty_fill='░') as bar:
                while len(items) < total_count:
                    r = self.get(**query, count=count, offset=offset)
                    items.extend(r.customers)
                    offset += count
                    bar.next(r.count)
            total_items.extend(items)
            current_first_contact_date += timedelta(days=days_count)
        return total_items

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
            phone=None,
            is_right_enabled=True
    ) -> List[dict]:

        if is_right_enabled and first_contact_date_to:
            first_contact_date_to += timedelta(days=1)
        if is_right_enabled and next_contact_date_to:
            next_contact_date_to += timedelta(days=1)
        if is_right_enabled and last_contact_date_to:
            last_contact_date_to += timedelta(days=1)
        total_items = []
        count = MAX_COUNT_CUSTOMERS_PER_REQUEST

        msk = pytz.timezone('Europe/Moscow')
        if first_contact_date_to is None:
            utc_time = datetime.utcnow()
            local_time = pytz.utc.localize(utc_time, is_dst=None).astimezone(msk)
            first_contact_date_to = local_time + timedelta(days=1)
        if first_contact_date_from is None:
            first_contact_date_from = pytz.utc.localize(
                datetime(year=2020, month=1, day=1), is_dst=None
            ).astimezone(msk)
            query = dict(
                first_contact_date_from=None,
                first_contact_date_to=first_contact_date_from,
                next_contact_date_from=next_contact_date_from,
                next_contact_date_to=next_contact_date_to,
                last_contact_date_from=last_contact_date_from,
                last_contact_date_to=last_contact_date_to,
                ids=ids,
                vk_ids=vk_ids,
                tags=tags,
                managers=managers,
                sources=sources,
                phone=phone,
                is_right_enabled=False
            )
            r = self.get(**query, count=1, offset=0)
            total_count = r.not_returned_count + r.count
            if total_count != 0:
                items = []
                offset = 0
                while len(items) < total_count:
                    r = self.get(**query, count=count, offset=offset)
                    items.extend(r.customers)
                    offset += count
                total_items.extend(items)

        if first_contact_date_to - first_contact_date_from > timedelta(days=7):
            days_count = 7
            query = dict(
                first_contact_date_from=first_contact_date_from,
                first_contact_date_to=first_contact_date_to - timedelta(days=days_count),
                next_contact_date_from=next_contact_date_from,
                next_contact_date_to=next_contact_date_to,
                last_contact_date_from=last_contact_date_from,
                last_contact_date_to=last_contact_date_to,
                ids=ids,
                vk_ids=vk_ids,
                tags=tags,
                managers=managers,
                sources=sources,
                phone=phone,
                is_right_enabled=False,
                days_count=days_count
            )
            total_items.extend(self.get_all_with_step(**query))
        else:
            days_count = 0

        if days_count == 0:
            new_first_contact_date_from = first_contact_date_from
        else:
            new_first_contact_date_from = first_contact_date_to - timedelta(days=days_count - 1)
        query = dict(
            first_contact_date_from=new_first_contact_date_from,
            first_contact_date_to=first_contact_date_to,
            next_contact_date_from=next_contact_date_from,
            next_contact_date_to=next_contact_date_to,
            last_contact_date_from=last_contact_date_from,
            last_contact_date_to=last_contact_date_to,
            ids=ids,
            vk_ids=vk_ids,
            tags=tags,
            managers=managers,
            sources=sources,
            phone=phone,
            is_right_enabled=False,
            days_count=1
        )
        total_items.extend(self.get_all_with_step(**query))

        return total_items


class CustomersResponse:
    def __init__(self, response: dict):
        self.count: int = response['count']
        self.not_returned_count: int = response['notReturnedCount']
        self.customers: list = response['customers']
        self.response: dict = response

    def __repr__(self):
        return str(self.response)
