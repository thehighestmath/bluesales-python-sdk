# bluesales-python-sdk

_Hint: Для того, чтобы BlueSales API работало вы **должны** иметь PRO акканут_

## Как использовать?

Получение __N__ клиентов с датой первого контакта от __first_contact_date_from__ до __first_contact_date_to__
```python
from datetime import datetime

from bluesalespy import BlueSales


def main():
    blue_sales = BlueSales('login', 'password')
    response = blue_sales.customers.get(
        first_contact_date_from=datetime(year=2020, month=12, day=31),
        first_contact_date_to=datetime(year=2020, month=12, day=31),
        count=500, offset=0
    )
    print(response)
    print(response.count)
    print(response.not_returned_count)
    for customer in response.customers:
        print(customer.id)
        print(customer.vk.id)
        print(customer.manager.full_name)


if __name__ == '__main__':
    main()
```

## Методы
- Получение списка клиентов (метод customers.get) 
- Сохранение / обновление клиента в BlueSales (методы customers.add / customers.update)
- Сохранение нескольких клиентов в BlueSales (метод customers.addMany)
- Обновление нескольких клиентов в BlueSales (метод customers.updateMany)
- Удаление клиента из BlueSales (метод customers.delete)
- Обновление статуса заказа (метод orders.setStatus)
- Получение списка заказов (метод orders.get) 
- Добавление заказа (метод orders.add)
- Массовое обновление заказов (метод orders.updateMany)
- Получение списка пользователей (метод users.get)

#### https://bluesales.ru/app/api/BlueSalesApiDemo/