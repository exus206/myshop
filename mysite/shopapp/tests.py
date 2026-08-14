# shopapp/tests.py

import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from shopapp.models import Product, Category, Order


class OrderDetailViewTestCase(TestCase):
    """Тесты для OrderDetailView"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@test.com'
        )
        content_type = ContentType.objects.get_for_model(Order)
        permission = Permission.objects.get(
            codename='view_order',
            content_type=content_type
        )
        cls.user.user_permissions.add(permission)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().tearDownClass()

    def setUp(self):
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

        self.category = Category.objects.create(name='Тестовая категория')
        self.product = Product.objects.create(
            name='Тестовый продукт',
            description='Описание',
            price=100,
            category=self.category
        )

        self.order = Order.objects.create(
            delivery_address='ул. Тестовая, д. 1',
            promocode='TEST123',
            user=self.user
        )
        self.order.products.add(self.product)

    def tearDown(self):
        self.order.delete()
        self.product.delete()
        self.category.delete()

    def test_order_details(self):
        """Проверка получения заказа"""
        response = self.client.get(
            reverse('shopapp:order_detail', kwargs={'pk': self.order.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order.delivery_address)
        self.assertContains(response, self.order.promocode)
        self.assertEqual(response.context['order'].pk, self.order.pk)


class OrdersExportTestCase(TestCase):
    """Тесты для экспорта заказов"""

    fixtures = [
        'users.json',
        'categories.json',
        'products.json',
        'orders.json',
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.first()
        if cls.user:
            cls.user.is_staff = True
            cls.user.set_password('testpass123')
            cls.user.save()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        self.client = Client()
        if self.user:
            self.client.login(username=self.user.username, password='testpass123')

    def test_orders_export(self):
        """Проверка экспорта заказов — сравниваем ответ API с данными из БД"""
        response = self.client.get(reverse('shopapp:orders_api_export'))

        self.assertEqual(response.status_code, 200)

        # Данные из API
        api_data = json.loads(response.content)

        # Формируем такую же структуру из БД
        orders_from_db = Order.objects.select_related('user').prefetch_related('products').all()
        expected_data = {
            'orders': [
                {
                    'id': order.id,
                    'delivery_address': order.delivery_address,
                    'promocode': order.promocode,
                    'user_id': order.user.id,
                    'product_ids': list(order.products.values_list('id', flat=True)),
                }
                for order in orders_from_db
            ]
        }

        # Одно сравнение для всех данных
        self.assertEqual(api_data, expected_data)

    def test_orders_export_not_staff(self):
        """Не-staff пользователь должен получить 403"""
        self.client.logout()
        user = User.objects.create_user(username='normal', password='normal123')
        self.client.login(username='normal', password='normal123')
        response = self.client.get(reverse('shopapp:orders_api_export'))
        self.assertEqual(response.status_code, 403)

    def test_orders_export_unauthorized(self):
        """Неавторизованный доступ должен вернуть 302"""
        self.client.logout()
        response = self.client.get(reverse('shopapp:orders_api_export'))
        self.assertEqual(response.status_code, 302)