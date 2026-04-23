# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Any


# ---------------------------------------------------------------------------
# Ответы API
# ---------------------------------------------------------------------------


@dataclass
class CustomersResponse:
    """Ответ на запрос customers.get."""

    count: int
    not_returned_count: int
    customers: list[dict]
    response: dict

    def __repr__(self) -> str:
        return (
            f"CustomersResponse(count={self.count}, "
            f"not_returned_count={self.not_returned_count})"
        )


@dataclass
class OrdersResponse:
    """Ответ на запрос orders.get."""

    count: int
    not_returned_count: int
    orders: list[dict]
    response: dict

    def __repr__(self) -> str:
        return (
            f"OrdersResponse(count={self.count}, "
            f"not_returned_count={self.not_returned_count})"
        )


# ---------------------------------------------------------------------------
# Входные модели
# ---------------------------------------------------------------------------


@dataclass(kw_only=True)
class Customer:
    """Модель клиента для передачи в :meth:`CustomersAPI.add` и :meth:`CustomersAPI.update`.

    Используйте :meth:`to_dict` для получения словаря, который принимает API.

    Example::

        from bluesalespy import BlueSales, Customer

        bs = BlueSales('login@example.com', 'password')

        customer = Customer(
            full_name='Иван Иванов',
            phone='79161234567',
            crm_status='Новый',
            source='Instagram',
            tag_ids=[1826732, 826312],
        )
        saved = bs.customers.add(customer.to_dict())
        print(saved['id'])
    """

    # --- Идентификатор (только для update) ---
    customer_id: int | None = None

    # --- Основная информация ---
    full_name: str | None = None
    birthday: str | None = None  # 'YYYY-MM-DD' или 'DD.MM.YYYY'
    sex: str | None = None  # 'male' / 'female'

    # --- Контактные данные ---
    phone: str | None = None  # только цифры, напр. '79161234567'
    email: str | None = None
    address: str | None = None
    other_contacts: str | None = None

    # --- Местоположение ---
    country: str | None = None
    city: str | None = None

    # --- ВКонтакте ---
    vk_id: str | None = None

    # --- Одноклассники ---
    ok_id: str | None = None

    # --- Instagram ---
    instagram_id: str | None = None
    instagram_login: str | None = None

    # --- WhatsApp ---
    whatsapp_id: str | None = None  # номер в формате '79161234567'

    # --- Telegram ---
    telegram_id: str | None = None
    telegram_login: str | None = None
    telegram_name: str | None = None

    # --- Facebook ---
    facebook_id: str | None = None
    facebook_name: str | None = None

    # --- CRM ---
    crm_status: str | None = None
    first_contact_date: str | None = None  # 'YYYY-MM-DD' или 'DD.MM.YYYY'
    next_contact_date: str | None = None
    source: str | None = None
    source_auto_create: bool = True
    sales_channel: str | None = None
    manager_login: str | None = None
    manager_name: str | None = None
    short_notes: str | None = None
    comments: str | None = None

    # --- Теги (полный набор — заменяет существующие) ---
    tag_ids: list[int] | None = None

    # --- Дополнительные поля ---
    custom_fields: list[dict] | None = None

    def to_dict(self) -> dict:
        """Преобразовать в словарь формата BlueSales API (camelCase, без None-полей)."""
        d: dict = {}

        if self.customer_id is not None:
            d["id"] = self.customer_id
        if self.full_name is not None:
            d["fullName"] = self.full_name
        if self.birthday is not None:
            d["birthday"] = self.birthday
        if self.sex is not None:
            d["sex"] = self.sex
        if self.phone is not None:
            d["phone"] = self.phone
        if self.email is not None:
            d["email"] = self.email
        if self.address is not None:
            d["address"] = self.address
        if self.other_contacts is not None:
            d["otherContacts"] = self.other_contacts
        if self.country is not None:
            d["country"] = {"name": self.country}
        if self.city is not None:
            d["city"] = {"name": self.city}
        if self.vk_id is not None:
            d["vk"] = {"id": self.vk_id, "name": ""}
        if self.ok_id is not None:
            d["ok"] = {"id": self.ok_id, "name": ""}
        if self.instagram_id is not None:
            d["instagram"] = {
                "id": self.instagram_id,
                "login": self.instagram_login or "",
            }
        if self.whatsapp_id is not None:
            d["whatsApp"] = {"id": self.whatsapp_id}
        if self.telegram_id is not None:
            d["telegram"] = {
                "id": self.telegram_id,
                "name": self.telegram_name or "",
                "login": self.telegram_login or "",
            }
        if self.facebook_id is not None:
            d["facebook"] = {
                "id": self.facebook_id,
                "name": self.facebook_name or "",
            }
        if self.crm_status is not None:
            d["crmStatus"] = {"name": self.crm_status}
        if self.first_contact_date is not None:
            d["firstContactDate"] = self.first_contact_date
        if self.next_contact_date is not None:
            d["nextContactDate"] = self.next_contact_date
        if self.source is not None:
            d["source"] = {"name": self.source, "autoCreate": self.source_auto_create}
        if self.sales_channel is not None:
            d["salesChannel"] = {"name": self.sales_channel}
        if self.manager_login is not None or self.manager_name is not None:
            d["manager"] = {
                "login": self.manager_login or "",
                "name": self.manager_name or "",
            }
        if self.short_notes is not None:
            d["shortNotes"] = self.short_notes
        if self.comments is not None:
            d["comments"] = self.comments
        if self.tag_ids is not None:
            d["tags"] = [{"id": tag_id} for tag_id in self.tag_ids]
        if self.custom_fields is not None:
            d["customFields"] = self.custom_fields

        return d


@dataclass(kw_only=True)
class Order:
    """Модель заказа для передачи в :meth:`OrdersAPI.add`.

    Используйте :meth:`to_dict` для получения словаря, который принимает API.

    Example::

        from bluesalespy import BlueSales, Order

        bs = BlueSales('login@example.com', 'password')

        order = Order(
            customer_id=1234567,
            date='2024-01-15',
            order_status='Новый',
            total=2500.0,
        )
        result = bs.orders.add(order.to_dict())
        print(result['id'])
    """

    customer_id: int | None = None
    date: str | None = None  # 'YYYY-MM-DD'
    order_status: str | None = None  # по имени
    order_status_id: int | None = None  # по id (приоритет над order_status)
    total: float | None = None
    prepay: float | None = None
    prepay_date: str | None = None  # 'YYYY-MM-DD'
    delivery_address: str | None = None
    comments: str | None = None
    manager_id: int | None = None
    payment_type_id: int | None = None
    custom_fields: list[dict] | None = None

    def to_dict(self) -> dict:
        """Преобразовать в словарь формата BlueSales API (camelCase, без None-полей)."""
        status: dict[str, Any] | None
        if self.order_status_id is not None:
            status = {"id": self.order_status_id}
        elif self.order_status is not None:
            status = {"name": self.order_status}
        else:
            status = None

        raw: dict[str, Any] = {
            "customerId": self.customer_id,
            "date": self.date,
            "orderStatus": status,
            "sum": self.total,
            "prepay": self.prepay,
            "prepayDate": self.prepay_date,
            "deliveryAddress": self.delivery_address,
            "comments": self.comments,
            "manager": {"id": self.manager_id} if self.manager_id is not None else None,
            "paymentType": {"id": self.payment_type_id}
            if self.payment_type_id is not None
            else None,
            "customFields": self.custom_fields,
        }
        return {k: v for k, v in raw.items() if v is not None}
