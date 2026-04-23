# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from typing import Any

from bluesalespy.exceptions import TooLargeBoarders
from bluesalespy.methods import CustomersMethods
from bluesalespy.models import CustomersResponse
from bluesalespy.request import RequestApi

_MSK = ZoneInfo("Europe/Moscow")
_EPOCH = datetime(2020, 1, 1, tzinfo=_MSK)
MAX_COUNT_CUSTOMERS_PER_REQUEST = 500


class CustomersAPI:
    def __init__(self, request_api: RequestApi) -> None:
        self.request_api = request_api

    def get(
        self,
        first_contact_date_from: datetime | None = None,
        first_contact_date_to: datetime | None = None,
        next_contact_date_from: datetime | None = None,
        next_contact_date_to: datetime | None = None,
        last_contact_date_from: datetime | None = None,
        last_contact_date_to: datetime | None = None,
        ids: list[int] | None = None,
        vk_ids: list[int] | None = None,
        count: int = 500,
        offset: int = 0,
        tags: list[str] | None = None,
        managers: list[int | str] | None = None,
        sources: list | None = None,
        phone: str | None = None,
        is_right_enabled: bool = True,
    ) -> "CustomersResponse":
        """Постраничное получение клиентов.

        Args:
            first_contact_date_from: дата первого контакта, от.
            first_contact_date_to: дата первого контакта, по.
            next_contact_date_from: дата следующего контакта, от.
            next_contact_date_to: дата следующего контакта, по.
            last_contact_date_from: дата последнего контакта, от.
            last_contact_date_to: дата последнего контакта, по.
            ids: список id клиентов.
            vk_ids: список ВКонтакте id.
            count: размер страницы (максимум 500).
            offset: смещение (номер первой строки).
            tags: фильтр по именам тегов.
            managers: фильтр по менеджерам — ``int`` (id) или ``str`` (login).
            sources: фильтр по источникам.
            phone: поиск по номеру телефона (только цифры).
            is_right_enabled: сдвигать правую границу дат на +1 день.

        Returns:
            :class:`CustomersResponse`

        Raises:
            TooLargeBoarders: если ``count > 500``.
            TypeError: если в ``managers`` передан неверный тип.
        """
        if count > MAX_COUNT_CUSTOMERS_PER_REQUEST:
            raise TooLargeBoarders(
                f"count должен быть не больше {MAX_COUNT_CUSTOMERS_PER_REQUEST}, получил {count}"
            )

        tags_out = [{"name": name} for name in (tags or [])]

        managers_out: list[dict] = []
        for manager in managers or []:
            if isinstance(manager, int):
                managers_out.append({"id": manager})
            elif isinstance(manager, str):
                managers_out.append({"login": manager})
            else:
                raise TypeError(f"Ожидалось int или str, получил {type(manager)}")

        if is_right_enabled:
            if first_contact_date_to:
                first_contact_date_to += timedelta(days=1)
            if next_contact_date_to:
                next_contact_date_to += timedelta(days=1)
            if last_contact_date_to:
                last_contact_date_to += timedelta(days=1)

        def _fmt(dt: datetime | None) -> str | None:
            return dt.strftime("%Y-%m-%d") if dt else None

        data = {
            "firstContactDateFrom": _fmt(first_contact_date_from),
            "firstContactDateTill": _fmt(first_contact_date_to),
            "nextContactDateFrom": _fmt(next_contact_date_from),
            "nextContactDateTill": _fmt(next_contact_date_to),
            "lastContactDateFrom": _fmt(last_contact_date_from),
            "lastContactDateTill": _fmt(last_contact_date_to),
            "ids": ids,
            "vkIds": vk_ids,
            "pageSize": count,
            "startRowNumber": offset,
            "tags": tags_out,
            "managers": managers_out,
            "sources": sources,
            "phone": phone,
        }
        response = self.request_api.send(CustomersMethods.get, data=data)
        return CustomersResponse(
            count=response["count"],
            not_returned_count=response["notReturnedCount"],
            customers=response["customers"],
            response=response,
        )

    def get_all_with_step(
        self,
        first_contact_date_from: datetime,
        first_contact_date_to: datetime,
        next_contact_date_from: datetime | None = None,
        next_contact_date_to: datetime | None = None,
        last_contact_date_from: datetime | None = None,
        last_contact_date_to: datetime | None = None,
        ids: list[int] | None = None,
        vk_ids: list[int] | None = None,
        tags: list[str] | None = None,
        managers: list[int | str] | None = None,
        sources: list | None = None,
        phone: str | None = None,
        is_right_enabled: bool = False,
        days_count: int = 1,
    ) -> list[dict]:
        """Получить клиентов постепенно, шагами по ``days_count`` дней."""
        total_items: list[dict] = []
        count = MAX_COUNT_CUSTOMERS_PER_REQUEST
        current_date = first_contact_date_from

        while current_date < first_contact_date_to:
            current_date_to = current_date + timedelta(days=days_count)
            query: Any = dict(
                first_contact_date_from=current_date,
                first_contact_date_to=current_date_to,
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
                is_right_enabled=is_right_enabled,
            )
            probe = self.get(**query, count=1, offset=0)
            total_count = probe.not_returned_count + probe.count

            if total_count > 0:
                items: list[dict] = []
                offset = 0
                while len(items) < total_count:
                    r = self.get(**query, count=count, offset=offset)
                    items.extend(r.customers)
                    offset += count
                total_items.extend(items)

            current_date += timedelta(days=days_count)

        return total_items

    def get_all(
        self,
        first_contact_date_from: datetime | None = None,
        first_contact_date_to: datetime | None = None,
        next_contact_date_from: datetime | None = None,
        next_contact_date_to: datetime | None = None,
        last_contact_date_from: datetime | None = None,
        last_contact_date_to: datetime | None = None,
        ids: list[int] | None = None,
        vk_ids: list[int] | None = None,
        tags: list[str] | None = None,
        managers: list[int | str] | None = None,
        sources: list | None = None,
        phone: str | None = None,
        is_right_enabled: bool = True,
    ) -> list[dict]:
        """Получить всех клиентов, автоматически постранично.

        Если диапазон дат больше 7 дней, запросы разбиваются на недельные
        интервалы для надёжности.

        Returns:
            Полный список клиентов.
        """
        if is_right_enabled and first_contact_date_to:
            first_contact_date_to += timedelta(days=1)
        if is_right_enabled and next_contact_date_to:
            next_contact_date_to += timedelta(days=1)
        if is_right_enabled and last_contact_date_to:
            last_contact_date_to += timedelta(days=1)

        total_items: list[dict] = []
        count = MAX_COUNT_CUSTOMERS_PER_REQUEST

        if first_contact_date_to is None:
            first_contact_date_to = datetime.now(_MSK) + timedelta(days=1)

        if first_contact_date_from is None:
            query: Any = dict(
                first_contact_date_from=None,
                first_contact_date_to=_EPOCH,
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
            )
            probe = self.get(**query, count=1, offset=0)
            if probe.not_returned_count + probe.count > 0:
                total_count = probe.not_returned_count + probe.count
                items: list[dict] = []
                offset = 0
                while len(items) < total_count:
                    r = self.get(**query, count=count, offset=offset)
                    items.extend(r.customers)
                    offset += count
                total_items.extend(items)
            first_contact_date_from = _EPOCH

        if first_contact_date_to - first_contact_date_from > timedelta(days=7):
            days_count = 7
            query = dict(
                first_contact_date_from=first_contact_date_from,
                first_contact_date_to=first_contact_date_to
                - timedelta(days=days_count),
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
                days_count=days_count,
            )
            total_items.extend(self.get_all_with_step(**query))
        else:
            days_count = 0

        new_first = (
            first_contact_date_from
            if days_count == 0
            else first_contact_date_to - timedelta(days=days_count - 1)
        )
        query = dict(
            first_contact_date_from=new_first,
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
            days_count=1,
        )
        total_items.extend(self.get_all_with_step(**query))
        return total_items

    def add(self, customer: dict) -> dict:
        """Добавить клиента.

        Args:
            customer: поля клиента (``fullName``, ``phone``, ``crmStatus``, ...).

        Returns:
            Сохранённый клиент с присвоенным ``id``.

        Example::

            bs.customers.add({
                'fullName': 'Иван Иванов',
                'phone': '79161234567',
                'crmStatus': {'name': 'Новый'},
                'source': {'name': 'Instagram', 'autoCreate': True},
            })
        """
        return self.request_api.send(CustomersMethods.add, data=customer)

    def update(self, customer: dict) -> dict:
        """Обновить клиента.

        Неуказанные поля остаются без изменений.

        Args:
            customer: обязательное поле ``id`` + изменяемые поля.

        Example::

            bs.customers.update({'id': 1234567, 'fullName': 'Новое имя'})
        """
        return self.request_api.send(CustomersMethods.update, data=customer)

    def add_many(self, customers: list[dict]) -> list[dict]:
        """Массовое добавление клиентов.

        Args:
            customers: список клиентов (те же поля, что в :meth:`add`).

        Returns:
            Список сохранённых клиентов с присвоенными id.
        """
        return self.request_api.send(CustomersMethods.add_many, data=customers)

    def update_many(self, customers: list[dict]) -> list[dict]:
        """Массовое обновление клиентов.

        Args:
            customers: каждый элемент должен содержать ``id`` и изменяемые поля.

        Returns:
            Список обновлённых клиентов.

        Example::

            bs.customers.update_many([
                {'id': 1234567, 'fullName': 'Иван Иванов'},
                {'id': 7654321, 'tags': [{'id': 1826732}, {'id': 826312}]},
            ])
        """
        return self.request_api.send(CustomersMethods.update_many, data=customers)

    def delete(self, customer_id: int) -> dict:
        """Удалить клиента.

        Args:
            customer_id: id клиента в BlueSales.
        """
        return self.request_api.send(CustomersMethods.delete, data={"id": customer_id})
