# -*- coding: utf-8 -*-
from enum import StrEnum


class CustomersMethods(StrEnum):
    get = "customers.get"
    add = "customers.add"
    update = "customers.update"
    add_many = "customers.addMany"
    update_many = "customers.updateMany"
    delete = "customers.delete"


class OrdersMethods(StrEnum):
    get = "orders.get"
    add = "orders.add"
    update_many = "orders.updateMany"
    set_status = "orders.setStatus"


class UsersMethods(StrEnum):
    get = "users.get"


class TagsMethods(StrEnum):
    add = "tags.add"
