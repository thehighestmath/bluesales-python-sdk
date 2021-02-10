# bluesales-python-sdk

_Hint: Для того, чтобы BlueSales API работало вы **должны** иметь PRO акканут_

## Как использовать?

Получение __N__ клиентов с датой первого контакта от __first_contact_date_from__ до __first_contact_date_to__
```python
from datetime import datetime

from bluesalespy import BlueSales


def main():
    blue_sales = BlueSales('login', 'password')
    response = blue_sales.customers.get_all(
        first_contact_date_from=datetime(year=2021, month=2, day=1),
        first_contact_date_to=datetime(year=2021, month=2, day=28),
    )
    print(response)


if __name__ == '__main__':
    main()
```
#### Для использования необходим python3.8

## Что необходимо для использования SDK

_unix script_

    git clone git@github.com:thehighestmath/bluesales-python-sdk.git
    cd bluesales-python-sdk
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

Для декактивации виртуального окружени
    
    deactivate

(опционально)
    
    sudo apt-get install python3-venv 


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
