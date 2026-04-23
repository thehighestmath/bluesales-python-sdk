# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from bluesalespy.exceptions import TooLargeBoarders
from bluesalespy.methods import OrdersMethods
from bluesalespy.models import OrdersResponse
from bluesalespy.request import RequestApi

MAX_COUNT_ORDERS_PER_REQUEST = 500


class OrdersAPI:
    def __init__(self, request_api: RequestApi) -> None:
        self.request_api = request_api

    def get(
        self,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        order_statuses: list[int | str] | None = None,
        ids: list[int] | None = None,
        internal_numbers: list[int] | None = None,
        customer_id: int | None = None,
        count: int = 500,
        offset: int = 0,
    ) -> "OrdersResponse":
        """Постраничное получение заказов.

        Args:
            date_from: дата заказа, от.
            date_to: дата заказа, по.
            order_statuses: фильтр по статусам — ``int`` (id) или ``str`` (название).
            ids: список id заказов.
            internal_numbers: внутренние номера заказов.
            customer_id: id клиента.
            count: размер страницы (максимум 500).
            offset: смещение.

        Returns:
            :class:`OrdersResponse`

        Raises:
            TooLargeBoarders: если ``count > 500``.
            TypeError: если в ``order_statuses`` передан неверный тип.
        """
        if count > MAX_COUNT_ORDERS_PER_REQUEST:
            raise TooLargeBoarders(
                f"count должен быть не больше {MAX_COUNT_ORDERS_PER_REQUEST}, получил {count}"
            )

        out_statuses: list[dict] = []
        for status in order_statuses or []:
            if isinstance(status, int):
                out_statuses.append({"id": status})
            elif isinstance(status, str):
                out_statuses.append({"name": status})
            else:
                raise TypeError(f"Ожидалось int или str, получил {type(status)}")

        data = {
            "dateFrom": date_from.strftime("%Y-%m-%d") if date_from else None,
            "dateTill": (date_to + timedelta(days=1)).strftime("%Y-%m-%d")
            if date_to
            else None,
            "orderStatuses": out_statuses,
            "customerId": customer_id,
            "ids": ids,
            "internalNumbers": internal_numbers,
            "pageSize": count,
            "startRowNumber": offset,
        }
        response = self.request_api.send(OrdersMethods.get, data=data)
        return OrdersResponse(
            count=response["count"],
            not_returned_count=response["notReturnedCount"],
            orders=response["orders"],
            response=response,
        )

    def get_all(
        self,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        order_statuses: list[int | str] | None = None,
        ids: list[int] | None = None,
        internal_numbers: list[int] | None = None,
        customer_id: int | None = None,
    ) -> list[dict]:
        """Получить все заказы, автоматически постранично.

        Returns:
            Полный список заказов.
        """
        count = MAX_COUNT_ORDERS_PER_REQUEST
        probe = self.get(
            date_from,
            date_to,
            order_statuses,
            ids,
            internal_numbers,
            customer_id,
            count=1,
            offset=0,
        )
        total_count = probe.not_returned_count + probe.count
        if total_count == 0:
            return []

        items: list[dict] = []
        offset = 0
        while len(items) < total_count:
            r = self.get(
                date_from,
                date_to,
                order_statuses,
                ids,
                internal_numbers,
                customer_id,
                count,
                offset,
            )
            items.extend(r.orders)
            offset += count
        return items

    def add(self, order: dict) -> dict:
        """Добавить заказ.

        Args:
            order: поля заказа.

        Returns:
            Созданный заказ с присвоенным ``id``.
        """
        return self.request_api.send(OrdersMethods.add, data=order)

    def set_status(
        self,
        order_id: int,
        order_status: str | None = None,
        post_tracking_number: str | None = None,
        post_status: str | None = None,
    ) -> dict:
        """Обновить статус заказа.

        Args:
            order_id: id заказа в BlueSales.
            order_status: новый статус заказа (название).
            post_tracking_number: трек-номер почтового отправления.
            post_status: статус почтового отправления.

        Returns:
            Обновлённый заказ.
        """
        data = {
            "id": order_id,
            "orderStatus": order_status,
            "postTrackingNumber": post_tracking_number,
            "postStatus": post_status,
        }
        return self.request_api.send(OrdersMethods.set_status, data=data)

    def update_many(
        self,
        ids: list[int],
        prepay: float | None = None,
        prepay_comments: str | None = None,
        payment_type_id: int | None = None,
        prepay_date: str | None = None,
        extra: dict | None = None,
    ) -> dict:
        """Массовое обновление заказов.

        Args:
            ids: список id заказов.
            prepay: сумма предоплаты.
            prepay_comments: комментарий к предоплате.
            payment_type_id: id способа оплаты.
            prepay_date: дата предоплаты (``'YYYY-MM-DD'``).
            extra: дополнительные поля (``orderStatus``, ``manager``, ``date``,
                ``customFieldValue`` и др.).

        Example::

            bs.orders.update_many(
                ids=[111, 222],
                prepay=500.0,
                payment_type_id=837291,
                extra={'orderStatus': {'id': 172946}},
            )
        """
        data: dict = {
            "ids": ids,
            "prepay": prepay,
            "prepayComments": prepay_comments,
            "paymentType": {"id": payment_type_id} if payment_type_id else None,
            "prepayDate": prepay_date,
        }
        if extra:
            data.update(extra)
        return self.request_api.send(OrdersMethods.update_many, data=data)
