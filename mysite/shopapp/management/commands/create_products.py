# shopapp/management/commands/create_products.py

from django.core.management.base import BaseCommand
from shopapp.models import Category, Product


class Command(BaseCommand):
    help = 'Создание продуктов через get_or_create'

    def handle(self, *args, **kwargs):
        electronics, created = Category.objects.get_or_create(
            name='Электроника',
            defaults={'description': 'Электронные устройства и гаджеты'}
        )

        clothing, created = Category.objects.get_or_create(
            name='Одежда',
            defaults={'description': 'Одежда и аксессуары'}
        )

        books, created = Category.objects.get_or_create(
            name='Книги',
            defaults={'description': 'Книги и учебные материалы'}
        )

        products_data = [
            {
                'name': 'Смартфон',
                'description': 'Современный смартфон с большим экраном и мощной камерой',
                'price': 29999.99,
                'discount': 10.00,
                'quantity': 50,
                'category': electronics,
                'in_stock': True,
                'archived': False
            },
            {
                'name': 'Ноутбук',
                'description': 'Мощный ноутбук для работы и развлечений',
                'price': 59999.99,
                'discount': 5.00,
                'quantity': 25,
                'category': electronics,
                'in_stock': True,
                'archived': False
            },
            {
                'name': 'Футболка',
                'description': 'Удобная футболка из натурального хлопка',
                'price': 1499.99,
                'discount': 15.00,
                'quantity': 100,
                'category': clothing,
                'in_stock': True,
                'archived': False
            },
            {
                'name': 'Джинсы',
                'description': 'Классические джинсы прямого кроя',
                'price': 3499.99,
                'discount': 20.00,
                'quantity': 75,
                'category': clothing,
                'in_stock': True,
                'archived': False
            },
            {
                'name': 'Наушники',
                'description': 'Беспроводные наушники с шумоподавлением',
                'price': 7999.99,
                'discount': 0.00,
                'quantity': 30,
                'category': electronics,
                'in_stock': True,
                'archived': False
            },
            {
                'name': 'Python для начинающих',
                'description': 'Учебник по программированию на Python',
                'price': 1299.99,
                'discount': 25.00,
                'quantity': 40,
                'category': books,
                'in_stock': True,
                'archived': False
            },
        ]

        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={k: v for k, v in product_data.items() if k != 'name'}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создан продукт: {product.name}'))
            else:
                self.stdout.write(f'Продукт уже существует: {product.name}')

        self.stdout.write(self.style.SUCCESS('Все продукты успешно созданы'))