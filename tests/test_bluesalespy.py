# -*- coding: utf-8 -*-
"""Unit-тесты для bluesalespy (без реальных HTTP-запросов)."""
from unittest.mock import MagicMock

import pytest

from bluesalespy import Customer, CustomersResponse, Order, OrdersResponse
from bluesalespy.bluesales import get_hash
from bluesalespy.customersapi import CustomersAPI
from bluesalespy.exceptions import TooLargeBoarders
from bluesalespy.methods import CustomersMethods, OrdersMethods, TagsMethods
from bluesalespy.ordersapi import OrdersAPI
from bluesalespy.request import RequestApi
from bluesalespy.tagsapi import TagsAPI


def make_mock_rq(**send_return) -> MagicMock:
    rq = MagicMock(spec=RequestApi)
    rq.login = 'test@example.com'
    rq.send.return_value = send_return or {}
    return rq


def customers_response_dict(**kwargs) -> dict:
    return {'count': 0, 'notReturnedCount': 0, 'customers': [], **kwargs}


def orders_response_dict(**kwargs) -> dict:
    return {'count': 0, 'notReturnedCount': 0, 'orders': [], **kwargs}


# ---------------------------------------------------------------------------
# Утилиты
# ---------------------------------------------------------------------------

def test_password_hash_is_uppercase_md5():
    # MD5("password") = 5f4dcc3b5aa765d61d8327deb882cf99
    assert get_hash('password') == '5F4DCC3B5AA765D61D8327DEB882CF99'


def test_password_hash_empty_string():
    assert get_hash('') == 'D41D8CD98F00B204E9800998ECF8427E'


# ---------------------------------------------------------------------------
# CustomersResponse dataclass
# ---------------------------------------------------------------------------

def test_customers_response_fields():
    customers = [{'id': 1}, {'id': 2}]
    resp = CustomersResponse(count=2, not_returned_count=5, customers=customers, response={})
    assert resp.count == 2
    assert resp.not_returned_count == 5
    assert resp.customers == customers


def test_customers_response_repr():
    resp = CustomersResponse(count=1, not_returned_count=0, customers=[], response={})
    assert 'count=1' in repr(resp)


# ---------------------------------------------------------------------------
# OrdersResponse dataclass
# ---------------------------------------------------------------------------

def test_orders_response_fields():
    orders = [{'id': 10}]
    resp = OrdersResponse(count=1, not_returned_count=0, orders=orders, response={})
    assert resp.orders == orders


# ---------------------------------------------------------------------------
# Customer dataclass
# ---------------------------------------------------------------------------

def test_customer_to_dict_omits_none():
    c = Customer(full_name='Иван')
    d = c.to_dict()
    assert d == {'fullName': 'Иван'}


def test_customer_to_dict_nested_objects():
    c = Customer(country='Россия', city='Москва', vk_id='123')
    d = c.to_dict()
    assert d['country'] == {'name': 'Россия'}
    assert d['city'] == {'name': 'Москва'}
    assert d['vk'] == {'id': '123', 'name': ''}


def test_customer_to_dict_crm_status():
    c = Customer(crm_status='Новый', source='Instagram')
    d = c.to_dict()
    assert d['crmStatus'] == {'name': 'Новый'}
    assert d['source'] == {'name': 'Instagram', 'autoCreate': True}


def test_customer_to_dict_tags():
    c = Customer(tag_ids=[100, 200])
    d = c.to_dict()
    assert d['tags'] == [{'id': 100}, {'id': 200}]


def test_customer_to_dict_manager():
    c = Customer(manager_login='mgr@example.com')
    d = c.to_dict()
    assert d['manager'] == {'login': 'mgr@example.com', 'name': ''}


def test_customer_id_for_update():
    c = Customer(customer_id=42, full_name='Новое имя')
    d = c.to_dict()
    assert d['id'] == 42
    assert d['fullName'] == 'Новое имя'


# ---------------------------------------------------------------------------
# Order dataclass
# ---------------------------------------------------------------------------

def test_order_to_dict_basic():
    o = Order(customer_id=1, date='2024-01-15', order_status='Новый', total=1500.0)
    d = o.to_dict()
    assert d['customerId'] == 1
    assert d['orderStatus'] == {'name': 'Новый'}
    assert d['sum'] == 1500.0


def test_order_status_id_takes_priority():
    o = Order(order_status='Новый', order_status_id=777)
    d = o.to_dict()
    assert d['orderStatus'] == {'id': 777}


def test_order_to_dict_omits_none():
    o = Order(customer_id=5)
    d = o.to_dict()
    assert 'date' not in d
    assert 'sum' not in d


# ---------------------------------------------------------------------------
# CustomersAPI
# ---------------------------------------------------------------------------

class TestCustomersAPIGet:
    def test_raises_when_count_exceeds_limit(self):
        api = CustomersAPI(make_mock_rq())
        with pytest.raises(TooLargeBoarders):
            api.get(count=501)

    def test_returns_customers_response(self):
        rq = make_mock_rq(**customers_response_dict(count=1, customers=[{'id': 1}]))
        api = CustomersAPI(rq)
        resp = api.get(count=1)
        assert isinstance(resp, CustomersResponse)
        assert resp.count == 1
        assert resp.customers == [{'id': 1}]

    def test_sends_correct_method(self):
        rq = make_mock_rq(**customers_response_dict())
        api = CustomersAPI(rq)
        api.get()
        call_method = rq.send.call_args[0][0]
        assert call_method == CustomersMethods.get

    def test_managers_int_converted_to_id(self):
        rq = make_mock_rq(**customers_response_dict())
        api = CustomersAPI(rq)
        api.get(managers=[42])
        sent_data = rq.send.call_args[1]['data']
        assert sent_data['managers'] == [{'id': 42}]

    def test_managers_str_converted_to_login(self):
        rq = make_mock_rq(**customers_response_dict())
        api = CustomersAPI(rq)
        api.get(managers=['ivan@example.com'])
        sent_data = rq.send.call_args[1]['data']
        assert sent_data['managers'] == [{'login': 'ivan@example.com'}]

    def test_managers_wrong_type_raises(self):
        api = CustomersAPI(make_mock_rq())
        with pytest.raises(TypeError):
            api.get(managers=[3.14])

    def test_tags_converted_to_name_dicts(self):
        rq = make_mock_rq(**customers_response_dict())
        api = CustomersAPI(rq)
        api.get(tags=['VIP', 'Москва'])
        sent_data = rq.send.call_args[1]['data']
        assert sent_data['tags'] == [{'name': 'VIP'}, {'name': 'Москва'}]


class TestCustomersAPIMutations:
    def test_add_calls_correct_method(self):
        rq = make_mock_rq(id=1, fullName='Иван')
        api = CustomersAPI(rq)
        result = api.add({'fullName': 'Иван'})
        rq.send.assert_called_once_with(CustomersMethods.add, data={'fullName': 'Иван'})
        assert result['id'] == 1

    def test_update_calls_correct_method(self):
        rq = make_mock_rq(id=42, fullName='Новое имя')
        api = CustomersAPI(rq)
        api.update({'id': 42, 'fullName': 'Новое имя'})
        rq.send.assert_called_once_with(
            CustomersMethods.update, data={'id': 42, 'fullName': 'Новое имя'}
        )

    def test_add_many_calls_correct_method(self):
        customers = [{'fullName': 'A'}, {'fullName': 'B'}]
        rq = make_mock_rq()
        rq.send.return_value = customers
        api = CustomersAPI(rq)
        api.add_many(customers)
        rq.send.assert_called_once_with(CustomersMethods.add_many, data=customers)

    def test_update_many_calls_correct_method(self):
        customers = [{'id': 1, 'fullName': 'X'}]
        rq = make_mock_rq()
        rq.send.return_value = customers
        api = CustomersAPI(rq)
        api.update_many(customers)
        rq.send.assert_called_once_with(CustomersMethods.update_many, data=customers)

    def test_delete_passes_id(self):
        rq = make_mock_rq()
        api = CustomersAPI(rq)
        api.delete(99)
        rq.send.assert_called_once_with(CustomersMethods.delete, data={'id': 99})


# ---------------------------------------------------------------------------
# OrdersAPI
# ---------------------------------------------------------------------------

class TestOrdersAPIGet:
    def test_raises_when_count_exceeds_limit(self):
        api = OrdersAPI(make_mock_rq())
        with pytest.raises(TooLargeBoarders):
            api.get(count=501)

    def test_returns_orders_response(self):
        rq = make_mock_rq(**orders_response_dict(count=2, orders=[{'id': 1}, {'id': 2}]))
        api = OrdersAPI(rq)
        resp = api.get()
        assert isinstance(resp, OrdersResponse)
        assert resp.count == 2
        assert len(resp.orders) == 2

    def test_status_int_converted_to_id(self):
        rq = make_mock_rq(**orders_response_dict())
        api = OrdersAPI(rq)
        api.get(order_statuses=[123])
        sent_data = rq.send.call_args[1]['data']
        assert sent_data['orderStatuses'] == [{'id': 123}]

    def test_status_str_converted_to_name(self):
        rq = make_mock_rq(**orders_response_dict())
        api = OrdersAPI(rq)
        api.get(order_statuses=['Новый'])
        sent_data = rq.send.call_args[1]['data']
        assert sent_data['orderStatuses'] == [{'name': 'Новый'}]

    def test_status_wrong_type_raises(self):
        api = OrdersAPI(make_mock_rq())
        with pytest.raises(TypeError):
            api.get(order_statuses=[3.14])


class TestOrdersAPIMutations:
    def test_add_calls_correct_method(self):
        rq = make_mock_rq(id=10)
        api = OrdersAPI(rq)
        api.add({'customerId': 1})
        rq.send.assert_called_once_with(OrdersMethods.add, data={'customerId': 1})

    def test_set_status_sends_all_fields(self):
        rq = make_mock_rq(id=5)
        api = OrdersAPI(rq)
        api.set_status(5, order_status='Доставлен', post_tracking_number='TN123')
        rq.send.assert_called_once_with(
            OrdersMethods.set_status,
            data={
                'id': 5,
                'orderStatus': 'Доставлен',
                'postTrackingNumber': 'TN123',
                'postStatus': None,
            },
        )

    def test_update_many_builds_payment_type(self):
        rq = make_mock_rq()
        api = OrdersAPI(rq)
        api.update_many(ids=[1, 2], payment_type_id=999)
        sent_data = rq.send.call_args[1]['data']
        assert sent_data['paymentType'] == {'id': 999}
        assert sent_data['ids'] == [1, 2]

    def test_update_many_merges_extra(self):
        rq = make_mock_rq()
        api = OrdersAPI(rq)
        api.update_many(ids=[3], extra={'orderStatus': {'id': 77}})
        sent_data = rq.send.call_args[1]['data']
        assert sent_data['orderStatus'] == {'id': 77}


# ---------------------------------------------------------------------------
# TagsAPI
# ---------------------------------------------------------------------------

class TestTagsAPI:
    def test_add_sends_correct_data(self):
        rq = make_mock_rq(id=42, name='VIP')
        api = TagsAPI(rq)
        result = api.add('VIP', add_to_beginning=True)
        rq.send.assert_called_once_with(
            TagsMethods.add, data={'name': 'VIP', 'addToBeginning': True}
        )
        assert result['id'] == 42

    def test_add_to_beginning_defaults_to_false(self):
        rq = make_mock_rq(id=1, name='Москва')
        api = TagsAPI(rq)
        api.add('Москва')
        sent_data = rq.send.call_args[1]['data']
        assert sent_data['addToBeginning'] is False
