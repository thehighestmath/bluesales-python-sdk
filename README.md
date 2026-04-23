# bluesales-python-sdk

Python SDK для [BlueSales CRM API](https://bluesales.ru/app/api/).

> **Требование:** PRO-аккаунт BlueSales.

> **Дисклеймер:** Meta Platforms Inc. признана экстремистской организацией и запрещена на территории Российской Федерации. Instagram и Facebook, упомянутые в документации, являются продуктами Meta.

## Установка

```bash
git clone https://github.com/thehighestmath/bluesales-python-sdk.git
cd bluesales-python-sdk
pip install -r requirements.txt
```

Или установить пакетом:

```bash
pip install .
```

## Быстрый старт

```python
from bluesalespy import BlueSales

bs = BlueSales('login@example.com', 'password')

# Получить пользователей (менеджеров)
users = bs.users.get()

# Добавить клиента
customer = bs.customers.add({
    'fullName': 'Иван Иванов',
    'phone': '79161234567',
    'crmStatus': {'name': 'Новый'},
})
print(customer['id'])
```

---

## API Reference

### `BlueSales(login, password)`

Основной класс. Принимает логин и пароль в открытом виде (пароль хешируется автоматически).

Атрибуты:

| Атрибут | Тип | Описание |
|---------|-----|----------|
| `customers` | `CustomersAPI` | Методы для работы с клиентами |
| `orders` | `OrdersAPI` | Методы для работы с заказами |
| `users` | `UsersAPI` | Методы для работы с пользователями |
| `tags` | `TagsAPI` | Методы для работы с тегами |

#### `call_api(method, data=None)`

Произвольный вызов любого метода API.

```python
result = bs.call_api('customers.get', data={'pageSize': 10, 'startRowNumber': 0})
```

---

### Клиенты — `bs.customers`

#### `get(...)` — постраничное получение

```python
from datetime import datetime

response = bs.customers.get(
    first_contact_date_from=datetime(2024, 1, 1),
    first_contact_date_to=datetime(2024, 12, 31),
    tags=['VIP'],
    managers=['manager@example.com'],  # или [1672] — id менеджера
    count=500,
    offset=0,
)

print(response.count)            # количество в текущей странице
print(response.not_returned_count)  # сколько ещё осталось
print(response.customers)        # список клиентов
```

Параметры:

| Параметр | Тип | Описание |
|----------|-----|----------|
| `first_contact_date_from` | `datetime` | Дата первого контакта, от |
| `first_contact_date_to` | `datetime` | Дата первого контакта, по |
| `next_contact_date_from` | `datetime` | Дата следующего контакта, от |
| `next_contact_date_to` | `datetime` | Дата следующего контакта, по |
| `last_contact_date_from` | `datetime` | Дата последнего контакта, от |
| `last_contact_date_to` | `datetime` | Дата последнего контакта, по |
| `ids` | `List[int]` | Список id клиентов |
| `vk_ids` | `List[int]` | Список ВКонтакте id |
| `count` | `int` | Размер страницы, максимум 500 |
| `offset` | `int` | Смещение (номер первой строки) |
| `tags` | `List[str]` | Фильтр по именам тегов |
| `managers` | `List[int\|str]` | Фильтр по менеджерам (id или login) |
| `sources` | `list` | Фильтр по источникам |
| `phone` | `str` | Поиск по телефону (только цифры) |

#### `get_all(...)` — получение всех с прогресс-баром

Те же параметры, что у `get`, без `count`/`offset`. Автоматически разбивает запросы на страницы.

```python
from datetime import datetime

customers = bs.customers.get_all(
    first_contact_date_from=datetime(2024, 1, 1),
    first_contact_date_to=datetime(2024, 12, 31),
)
print(len(customers))
```

#### `add(customer)` — добавить клиента

```python
customer = bs.customers.add({
    'fullName': 'Иван Иванов',
    'phone': '79161234567',
    'email': 'ivan@example.com',
    'birthday': '1990-05-15',
    'sex': 'male',
    'country': {'name': 'Россия'},
    'city': {'name': 'Москва'},

    # Аккаунты в соцсетях
    'vk': {'id': '123456', 'name': ''},
    'ok': {'id': '564849836025', 'name': ''},
    # 'instagram': {'id': '847932421', 'login': 'ivan.ivanov'},
    # 'whatsApp': {'id': '79161234567'},
    # 'telegram': {'id': '8473929', 'login': 'ivan1995'},
    # 'facebook': {'id': '49397234'},

    # CRM-информация
    'crmStatus': {'name': 'Новый'},
    'firstContactDate': '2024-01-15',
    'nextContactDate': '2024-02-01',
    'source': {'name': 'Instagram', 'autoCreate': True},
    'salesChannel': {'name': 'Интернет'},
    'manager': {'login': 'manager@example.com'},
    'shortNotes': 'Краткая заметка',
    'comments': 'Подробный комментарий',

    # Теги (полный набор — заменяет существующие)
    'tags': [{'id': 1826732}, {'id': 826312}],

    # Дополнительные поля
    # 'customFields': [{'fieldId': 3874632, 'value': 'значение'}],
})
print(customer['id'])
```

#### `update(customer)` — обновить клиента

Передаётся только `id` и изменяемые поля. Остальные поля остаются без изменений.

```python
bs.customers.update({
    'id': 1234567,
    'fullName': 'Новое имя',
})
```

#### `add_many(customers)` — массовое добавление

```python
saved = bs.customers.add_many([
    {'fullName': 'Иван Иванов', 'firstContactDate': '2024-01-15'},
    {'fullName': 'Пётр Петров', 'firstContactDate': '2024-01-15'},
])
```

#### `update_many(customers)` — массовое обновление

```python
bs.customers.update_many([
    {'id': 1234567, 'fullName': 'Новое имя'},
    {'id': 7654321, 'tags': [{'id': 1826732}, {'id': 826312}]},
])
```

> Теги передаются как полный набор — он заменит существующие теги клиента.

#### `delete(customer_id)` — удалить клиента

```python
bs.customers.delete(1234567)
```

---

### Заказы — `bs.orders`

#### `get(...)` — постраничное получение

```python
from datetime import datetime

response = bs.orders.get(
    date_from=datetime(2024, 1, 1),
    date_to=datetime(2024, 1, 31),
    order_statuses=['Новый', 'В работе'],  # или [837291, 172946] — id статусов
    customer_id=1234567,
    count=500,
    offset=0,
)

print(response.count)
print(response.orders)
```

Параметры:

| Параметр | Тип | Описание |
|----------|-----|----------|
| `date_from` | `datetime` | Дата заказа, от |
| `date_to` | `datetime` | Дата заказа, по |
| `order_statuses` | `List[int\|str]` | Фильтр по статусам (id или название) |
| `ids` | `List[int]` | Список id заказов |
| `internal_numbers` | `List[int]` | Внутренние номера заказов |
| `customer_id` | `int` | Id клиента |
| `count` | `int` | Размер страницы, максимум 500 |
| `offset` | `int` | Смещение |

#### `get_all(...)` — получение всех с прогресс-баром

Те же параметры, что у `get`, без `count`/`offset`.

```python
orders = bs.orders.get_all(
    date_from=datetime(2024, 1, 1),
    date_to=datetime(2024, 12, 31),
)
```

#### `add(order)` — добавить заказ

```python
order = bs.orders.add({
    'customerId': 1234567,
    'date': '2024-01-15',
    'orderStatus': {'name': 'Новый'},
    'sum': 1500.0,
})
print(order['id'])
```

#### `set_status(order_id, ...)` — обновить статус заказа

```python
bs.orders.set_status(
    order_id=9876543,
    order_status='Доставлен',
    post_tracking_number='RA123456789RU',
    post_status='Вручено',
)
```

#### `update_many(ids, ...)` — массовое обновление заказов

```python
bs.orders.update_many(
    ids=[111111, 222222],
    prepay=500.0,
    prepay_comments='Предоплата получена',
    payment_type_id=837291,
    prepay_date='2024-01-20',
    # Дополнительные поля через extra:
    extra={
        'orderStatus': {'id': 172946},
        'manager': {'id': 1672},
    },
)
```

---

### Пользователи — `bs.users`

#### `get()` — список пользователей (менеджеров)

```python
users = bs.users.get()
```

---

### Теги — `bs.tags`

#### `add(name, add_to_beginning=False)` — добавить тег

```python
tag = bs.tags.add('VIP', add_to_beginning=True)
print(tag['id'])
```

---

## Исключения

| Исключение | Описание |
|-----------|----------|
| `BlueSalesError` | Общая ошибка API |
| `WrongLoginOrPassword` | Неверный логин или пароль |
| `HttpError` | Сетевая ошибка при подключении |
| `TooLargeBoarders` | Запрошено больше 500 записей за раз |

```python
from bluesalespy import BlueSales, WrongLoginOrPassword, HttpError

try:
    bs = BlueSales('login@example.com', 'wrong_password')
    bs.users.get()
except WrongLoginOrPassword:
    print('Неверный логин или пароль')
except HttpError:
    print('Ошибка подключения к API')
```

---

## Разработка

```bash
pip install pytest
pytest bluesalespy/test_sample.py -v
```

## Требования

- Python 3.8+
- PRO-аккаунт BlueSales
