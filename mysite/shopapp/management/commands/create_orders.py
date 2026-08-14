# shopapp/management/commands/create_orders.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from shopapp.models import Product, Order


class Command(BaseCommand):
    help = 'Создание заказов через get_or_create'

    def handle(self, *args, **kwargs):
        if not User.objects.exists():
            self.stdout.write(self.style.ERROR('Нет пользователей! Создайте суперпользователя!'))
            return

        if not Product.objects.exists():
            self.stdout.write(self.style.ERROR('Нет продуктов! Сначала создайте продукты!'))
            return

        user = User.objects.first()

        smartphone = Product.objects.filter(name='Смартфон').first()
        notebook = Product.objects.filter(name='Ноутбук').first()
        tshirt = Product.objects.filter(name='Футболка').first()
        jeans = Product.objects.filter(name='Джинсы').first()
        headphones = Product.objects.filter(name='Наушники').first()
        book = Product.objects.filter(name='Python для начинающих').first()

        orders_data = [
            {
                'delivery_address': 'г. Москва, ул. Ленина, д. 1, кв. 10',
                'promocode': 'SALE2024',
                'products': [smartphone, headphones]
            },
            {
                'delivery_address': 'г. Санкт-Петербург, Невский пр., д. 50, кв. 25',
                'promocode': '',
                'products': [tshirt, jeans]
            },
            {
                'delivery_address': 'г. Екатеринбург, ул. Мира, д. 15, кв. 5',
                'promocode': 'DISCOUNT10',
                'products': [notebook, book]
            },
            {
                'delivery_address': 'г. Казань, ул. Баумана, д. 30, кв. 3',
                'promocode': 'NEWYEAR',
                'products': [smartphone, tshirt, book]
            },
        ]

        for order_data in orders_data:
            order, created = Order.objects.get_or_create(
                delivery_address=order_data['delivery_address'],
                user=user,
                defaults={'promocode': order_data['promocode']}
            )

            if created:
                products = [p for p in order_data['products'] if p is not None]
                if products:
                    order.products.add(*products)
                self.stdout.write(self.style.SUCCESS(f'Создан заказ #{order.id}'))
            else:
                self.stdout.write(f'Заказ уже существует: #{order.id}')

        self.stdout.write(self.style.SUCCESS('Все заказы успешно созданы'))