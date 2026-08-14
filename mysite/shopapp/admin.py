# shopapp/admin.py

import csv
from io import TextIOWrapper
from django.contrib import admin, messages
from django.shortcuts import render, redirect
from django.urls import path
from django.utils.translation import gettext_lazy as _
from .models import Category, Product, Order
from .forms import CSVImportForm


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


class OrderInline(admin.TabularInline):
    model = Order.products.through
    extra = 0
    verbose_name = 'Заказ'
    verbose_name_plural = 'Заказы'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'discount', 'quantity', 'category', 'in_stock', 'archived', 'created_at']
    list_filter = ['category', 'in_stock', 'archived']
    search_fields = ['name', 'description', 'price']
    actions = ['archive_products', 'unarchive_products']

    fieldsets = [
        (None, {'fields': ['name', 'description']}),
        (_('Цена и скидка'), {'fields': ['price', 'discount']}),
        (_('Дополнительные опции'), {'fields': ['archived'], 'classes': ['collapse']}),
        (_('Наличие'), {'fields': ['quantity', 'in_stock']}),
        (_('Категория'), {'fields': ['category']}),
    ]

    inlines = [OrderInline]

    @admin.action(description='Архивировать выбранные продукты')
    def archive_products(self, request, queryset):
        updated = queryset.update(archived=True)
        self.message_user(request, f'{updated} продуктов успешно архивировано.', messages.SUCCESS)

    @admin.action(description='Разархивировать выбранные продукты')
    def unarchive_products(self, request, queryset):
        updated = queryset.update(archived=False)
        self.message_user(request, f'{updated} продуктов успешно разархивировано.', messages.SUCCESS)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at', 'promocode', 'get_products_count']
    list_filter = ['created_at', 'user']
    search_fields = ['delivery_address', 'promocode', 'id']
    filter_horizontal = ['products']
    readonly_fields = ['created_at']
    change_list_template = 'admin/shopapp/orders_changelist.html'

    fieldsets = [
        (None, {'fields': ['user', 'delivery_address']}),
        (_('Детали заказа'), {'fields': ['products', 'promocode']}),
        (_('Дата'), {'fields': ['created_at']}),
    ]

    def get_products_count(self, obj):
        return obj.products.count()
    get_products_count.short_description = 'Количество товаров'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.admin_site.admin_view(self.import_csv), name='order_import_csv'),
        ]
        return custom_urls + urls

    def import_csv(self, request):
        if request.method == 'POST':
            form = CSVImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = TextIOWrapper(request.FILES['csv_file'].file, encoding='utf-8')
                reader = csv.reader(csv_file)
                next(reader, None)
                created = 0
                for row in reader:
                    if len(row) >= 4:
                        delivery_address, promocode, user_id, product_ids_str = row[0], row[1], row[2], row[3]
                        order = Order.objects.create(
                            delivery_address=delivery_address,
                            promocode=promocode,
                            user_id=int(user_id)
                        )
                        product_ids = [int(pid) for pid in product_ids_str.split(';') if pid.strip().isdigit()]
                        order.products.add(*product_ids)
                        created += 1
                messages.success(request, f'Импортировано заказов: {created}')
                return redirect('..')
        else:
            form = CSVImportForm()

        return render(request, 'admin/csv_form.html', {
            'form': form,
            'title': 'Импорт заказов',
            'opts': self.model._meta,
        })