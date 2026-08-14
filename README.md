# MyShop — интернет-магазин на Django

Полнофункциональный интернет-магазин, разработанный на Django 4.2.

## Возможности

### Магазин
- Каталог товаров с категориями
- Просмотр, создание, обновление и архивация товаров
- Поиск и фильтрация товаров
- RSS-лента последних товаров
- Sitemap

### Заказы
- Создание, просмотр, обновление и удаление заказов
- Привязка заказов к пользователям и товарам
- Экспорт заказов в JSON
- Импорт заказов из CSV через админку
- Просмотр заказов конкретного пользователя

### Пользователи
- Регистрация, вход и выход
- Профиль с аватаром
- Права доступа (создание, редактирование товаров)
- Список пользователей

### API
- REST API на Django REST Framework
- Пагинация
- Фильтрация и поиск

### Дополнительно
- Загрузка файлов (до 1 МБ)
- Cookies и сессии
- Кэширование
- Тесты

## Технологии

- Django 4.2
- Django REST Framework
- django-filter
- Pillow
- SQLite

## Установка

```bash
git clone https://github.com/exus206/myshop.git
cd myshop/mysite
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Деплой с Docker

```bash
docker compose up -d --build
```

Приложение будет доступно на `http://localhost:8000/`

## Лицензия

MIT