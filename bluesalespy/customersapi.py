# -*- coding: utf-8 -*-
from datetime import datetime
from .methods import CustomersMethods
from .request import RequestApi
from .exceptions import TooLargeBoarders

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
            ids=None,
            vk_ids=None,
            count: int = 500,
            offset: int = 0,
            tags=None,
            managers=None,
            sources=None,
            phone=None
    ):
        if count > MAX_COUNT_CUSTOMERS_PER_REQUEST:
            raise TooLargeBoarders('Количество запрашиваемых клиентов за раз должно быть меньше {MAX_COUNT}')
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
            'managers': managers,
            'sources': sources,
            'phone': phone,
        }

        response = self.request_api.send(
            CustomersMethods.get,
            data=data
        )

        return CustomersResponse(response)


class CrmStatus:
    def __init__(self, crm_status_json: dict):
        self.id: int = crm_status_json['id']
        self.name: str = crm_status_json['name']
        self.color: str = crm_status_json['color']
        self.crm_status_json: dict = crm_status_json

    def __repr__(self):
        return self.crm_status_json


class Vk:
    def __init__(self, vk: dict):
        self.id: int = vk['id']
        self.name: str = vk['name']
        self.messages_group_id: str = vk['messagesGroupId']
        self.vk: dict = vk

    def __repr__(self):
        return self.vk


class Manager:
    def __init__(self, manager_json: dict):
        self.id: int = manager_json['id'] if manager_json else None
        self.full_name = manager_json['fullName'] if manager_json else None
        self.email: str = manager_json['email'] if manager_json else None
        self.login: str = manager_json['login'] if manager_json else None
        self.phone: str = manager_json['phone'] if manager_json else None
        self.vk: str = manager_json['vk'] if manager_json else None
        self.manager_json: dict = manager_json

    def __repr__(self):
        return str(self.manager_json)


class Tag:
    def __init__(self, tag_json: dict):
        self.id: int = tag_json['id']
        self.name: str = tag_json['name']
        self.tag_json: dict = tag_json

    def __repr__(self):
        return str(self.tag_json)


class CustomField:
    def __init__(self, custom_field: dict):
        self.id: int = custom_field['fieldId']
        self.value = custom_field['value']
        self.value_as_text = custom_field['valueAsText']
        self.custom_field: dict = custom_field


class Customer:
    __slots__ = (
        'id', 'full_name', 'photo_url', 'country', 'city', 'birthday',
        'sex', 'vk', 'ok', 'facebook', 'instagram', 'whats_app',
        'phone', 'email', 'address', 'other_contacts', 'crm_status',
        'tags', 'first_contact_date', 'last_contact_date',
        'next_contact_date', 'source', 'sales_channel',
        'manager', 'vk_manager', 'ok_manager', 'short_notes', 'comments',
        'custom_fields', 'customer_json'
    )

    def __init__(self, customer_json):
        self.id: int = customer_json['id']
        self.full_name: str = customer_json['fullName']
        self.photo_url: str = customer_json['photoUrl']
        self.country = customer_json['country']
        self.city = customer_json['city']
        self.birthday = customer_json['birthday']
        self.sex: str = customer_json['sex']
        self.vk: Vk = Vk(customer_json['vk'])
        self.ok = None
        self.facebook = None
        self.whats_app = None
        self.phone: str = customer_json['phone']
        self.email: str = customer_json['email']
        self.address: str = customer_json['address']
        self.other_contacts: str = customer_json['otherContacts']
        self.crm_status: CrmStatus = CrmStatus(customer_json['crmStatus'])
        self.tags = [Tag(tag_json) for tag_json in customer_json['tags']]
        self.first_contact_date: str = customer_json['firstContactDate']
        self.last_contact_date: str = customer_json['lastContactDate']
        self.next_contact_date: str = customer_json['nextContactDate']
        self.source = customer_json['source']
        self.sales_channel = customer_json['salesChannel']
        self.manager: Manager = Manager(customer_json['manager'])
        self.vk_manager = None
        self.ok_manager = None
        self.short_notes = customer_json['shortNotes']
        self.comments = customer_json['comments']
        self.custom_fields = [customer_json['customFields']]

        self.customer_json: dict = customer_json

    def __repr__(self):
        return str(self.customer_json)


class CustomersResponse:
    def __init__(self, response: dict):
        self.count: int = response['count']
        self.not_returned_count: int = response['notReturnedCount']
        self.customers: list = [Customer(customer_json) for customer_json in response['customers']]
        self.response: dict = response

    def __repr__(self):
        return str(self.response)
