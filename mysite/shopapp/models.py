# shopapp/models.py

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название категории')
    description = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название товара')
    description = models.TextField(verbose_name='Описание товара')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='Скидка (%)')
    quantity = models.PositiveSmallIntegerField(default=0, verbose_name='Количество на складе')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    in_stock = models.BooleanField(default=True, verbose_name='В наличии')
    archived = models.BooleanField(default=False, verbose_name='Архивирован')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Создатель')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']
        permissions = [
            ('can_create_product', 'Может создавать продукт'),
            ('can_edit_product', 'Может редактировать продукт'),
        ]

    def get_absolute_url(self):
        return reverse('shopapp:product_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name


class Order(models.Model):
    delivery_address = models.TextField(verbose_name='Адрес доставки')
    promocode = models.CharField(max_length=50, blank=True, verbose_name='Промокод')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    products = models.ManyToManyField(Product, verbose_name='Товары')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ #{self.id} от {self.created_at.strftime("%d.%m.%Y")}'