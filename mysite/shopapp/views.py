# shopapp/views.py

import os
from datetime import datetime

from django.contrib.auth.models import User
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View, TemplateView
)
from django.core.cache import cache
from django.http import JsonResponse, Http404
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from .serializers import OrderSerializer

from .models import Product, Category, Order
from .forms import FileUploadForm, ProductForm, OrderForm

from django.contrib.syndication.views import Feed

class LatestProductsFeed(Feed):
    title = 'Latest Products'
    link = '/shop/products/'
    description = 'New products in shop'

    def items(self):
        return Product.objects.filter(archived=False).order_by('-created_at')[:10]

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.description[:200]

    def item_link(self, item):
        return item.get_absolute_url()


# ============================================
# Главная страница
# ============================================

class ShopIndexView(TemplateView):
    template_name = 'shopapp/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Главная страница магазина',
            'pages': [
                {'name': 'Список товаров', 'url': 'shopapp:product_list'},
                {'name': 'Создать товар', 'url': 'shopapp:create_product'},
                {'name': 'Список заказов', 'url': 'shopapp:order_list'},
                {'name': 'Создать заказ', 'url': 'shopapp:create_order'},
                {'name': 'Загрузка файла', 'url': 'shopapp:upload_file'},
                {'name': 'Загруженные файлы', 'url': 'shopapp:file_list'},
            ],
            'shop_name': 'MyShop',
            'current_date': datetime.now(),
        })
        return context


# ============================================
# Продукты
# ============================================

class ProductListView(ListView):
    """Список только неархивированных продуктов"""
    model = Product
    template_name = 'shopapp/products.html'
    context_object_name = 'products'
    queryset = Product.objects.filter(archived=False).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Магазин товаров',
            'categories': Category.objects.all(),
            'total_products': self.get_queryset().count(),
            'current_date': datetime.now(),
            'shop_name': 'MyShop',
        })
        return context


class ProductDetailView(DetailView):
    """Детали продукта"""
    model = Product
    template_name = 'shopapp/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Товар: {self.object.name}'
        return context


class ProductCreateView(PermissionRequiredMixin, CreateView):
    """Создание продукта (только с правом can_create_product)"""
    model = Product
    form_class = ProductForm
    template_name = 'shopapp/create_product.html'
    success_url = reverse_lazy('shopapp:product_list')
    permission_required = 'shopapp.can_create_product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание товара'
        return context

    def form_valid(self, form):
        form.instance.created_by = self.request.user  # Привязываем создателя
        messages.success(self.request, f'Товар "{form.instance.name}" успешно создан!')
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    """Обновление продукта (суперпользователь всегда, остальные — автор с правом)"""
    model = Product
    form_class = ProductForm
    template_name = 'shopapp/create_product.html'

    def get_success_url(self):
        return reverse('shopapp:product_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Обновление: {self.object.name}'
        return context

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        if request.user.has_perm('shopapp.can_edit_product') and obj.created_by == request.user:
            return super().dispatch(request, *args, **kwargs)
        messages.error(request, 'У вас нет прав на редактирование этого товара.')
        return redirect('shopapp:product_list')

    def form_valid(self, form):
        messages.success(self.request, f'Товар "{form.instance.name}" обновлён!')
        return super().form_valid(form)


class ProductArchiveView(View):
    """Архивация продукта (GET - подтверждение, POST - архивация)"""
    template_name = 'shopapp/product_archive.html'

    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        return render(request, self.template_name, {
            'title': f'Архивация: {product.name}',
            'product': product,
        })

    def post(self, request, pk):
        product = Product.objects.get(pk=pk)
        product.archived = True
        product.save()
        messages.success(request, f'Товар "{product.name}" архивирован!')
        return redirect('shopapp:product_list')


# ============================================
# Заказы
# ============================================

class OrderListView(ListView):
    """Список заказов"""
    model = Order
    template_name = 'shopapp/orders.html'
    context_object_name = 'orders'
    queryset = Order.objects.select_related('user').prefetch_related('products').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Список заказов',
            'shop_name': 'MyShop',
            'current_date': datetime.now(),
        })
        return context


class OrderDetailView(DetailView):
    """Детали заказа"""
    model = Order
    template_name = 'shopapp/order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        return Order.objects.select_related('user').prefetch_related('products')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Заказ #{self.object.id}'
        context['products_count'] = self.object.products.count()
        return context


class OrderCreateView(CreateView):
    """Создание заказа"""
    model = Order
    form_class = OrderForm
    template_name = 'shopapp/create_order.html'
    success_url = reverse_lazy('shopapp:order_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание заказа'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Заказ успешно создан!')
        return super().form_valid(form)


class OrderUpdateView(UpdateView):
    """Обновление заказа"""
    model = Order
    form_class = OrderForm
    template_name = 'shopapp/create_order.html'

    def get_success_url(self):
        return reverse('shopapp:order_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Обновление заказа #{self.object.id}'
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Заказ #{self.object.id} обновлён!')
        return super().form_valid(form)


class OrderDeleteView(DeleteView):
    """Удаление заказа (GET - подтверждение, POST - удаление)"""
    model = Order
    template_name = 'shopapp/order_delete.html'
    success_url = reverse_lazy('shopapp:order_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Удаление заказа #{self.object.id}'
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Заказ #{self.object.id} удалён!')
        return super().form_valid(form)


# ============================================
# Файлы
# ============================================

class FileUploadView(View):
    """Загрузка файлов"""
    template_name = 'shopapp/upload_file.html'

    def get(self, request):
        form = FileUploadForm()
        return render(request, self.template_name, {
            'title': 'Загрузка файла',
            'form': form,
            'max_file_size': settings.MAX_UPLOAD_SIZE // (1024 * 1024),
        })

    def post(self, request):
        form = FileUploadForm(request.POST, request.FILES)
        message = None
        message_type = None

        if form.is_valid():
            uploaded_file = request.FILES['file']
            if uploaded_file.size > settings.MAX_UPLOAD_SIZE:
                message = f'Ошибка! Размер файла ({uploaded_file.size / 1024:.1f} КБ) превышает 1 МБ.'
                message_type = 'error'
            else:
                file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)
                message = f'Файл "{uploaded_file.name}" успешно загружен!'
                message_type = 'success'
                form = FileUploadForm()

        return render(request, self.template_name, {
            'title': 'Загрузка файла',
            'form': form,
            'message': message,
            'message_type': message_type,
            'max_file_size': settings.MAX_UPLOAD_SIZE // (1024 * 1024),
        })


class FileListView(TemplateView):
    """Список загруженных файлов"""
    template_name = 'shopapp/file_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        media_dir = settings.MEDIA_ROOT
        files = []

        if os.path.exists(media_dir):
            for filename in os.listdir(media_dir):
                file_path = os.path.join(media_dir, filename)
                if os.path.isfile(file_path):
                    file_size = os.path.getsize(file_path)
                    files.append({
                        'name': filename,
                        'size': file_size,
                        'size_display': self._format_size(file_size),
                        'modified': datetime.fromtimestamp(os.path.getmtime(file_path)),
                        'url': os.path.join(settings.MEDIA_URL, filename)
                    })

        files.sort(key=lambda x: x['modified'], reverse=True)

        context.update({
            'title': 'Загруженные файлы',
            'files': files,
            'total_files': len(files),
        })
        return context

    @staticmethod
    def _format_size(size_bytes):
        if size_bytes < 1024:
            return f'{size_bytes} Б'
        elif size_bytes < 1024 * 1024:
            return f'{size_bytes / 1024:.1f} КБ'
        elif size_bytes < 1024 * 1024 * 1024:
            return f'{size_bytes / (1024 * 1024):.1f} МБ'
        else:
            return f'{size_bytes / (1024 * 1024 * 1024):.2f} ГБ'


class ProductCreateView(PermissionRequiredMixin, CreateView):
    """Создание продукта (только с правом can_create_product)"""
    model = Product
    form_class = ProductForm
    template_name = 'shopapp/create_product.html'
    success_url = reverse_lazy('shopapp:product_list')
    permission_required = 'shopapp.can_create_product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание товара'
        return context

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, f'Товар "{form.instance.name}" успешно создан!')
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Обновление продукта (суперпользователь всегда, остальные — автор с правом)"""
    model = Product
    form_class = ProductForm
    template_name = 'shopapp/create_product.html'

    def test_func(self):
        obj = self.get_object()
        user = self.request.user
        # Суперпользователь может всегда
        if user.is_superuser:
            return True
        # Остальные — только если есть право и они автор
        return user.has_perm('shopapp.can_edit_product') and obj.created_by == user

    def handle_no_permission(self):
        messages.error(self.request, 'У вас нет прав на редактирование этого товара.')
        return redirect('shopapp:product_list')

    def get_success_url(self):
        return reverse('shopapp:product_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Обновление: {self.object.name}'
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Товар "{form.instance.name}" обновлён!')
        return super().form_valid(form)


class OrdersExportApiView(UserPassesTestMixin, View):
    """API экспорт заказов в JSON (только для is_staff)"""

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request):
        orders = Order.objects.select_related('user').prefetch_related('products').all()
        orders_data = []
        for order in orders:
            orders_data.append({
                'id': order.id,
                'delivery_address': order.delivery_address,
                'promocode': order.promocode,
                'user_id': order.user.id,
                'product_ids': list(order.products.values_list('id', flat=True)),
            })
        return JsonResponse({'orders': orders_data}, json_dumps_params={'ensure_ascii': False})


class OrdersExportView(UserPassesTestMixin, TemplateView):
    """HTML страница экспорта заказов (только для is_staff)"""
    template_name = 'shopapp/orders_export.html'

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orders = Order.objects.select_related('user').prefetch_related('products').all()
        orders_data = []
        for order in orders:
            orders_data.append({
                'id': order.id,
                'delivery_address': order.delivery_address,
                'promocode': order.promocode,
                'user': order.user.username,
                'products': list(order.products.values_list('name', flat=True)),
            })
        context['title'] = 'Экспорт заказов'
        context['orders_json'] = orders_data
        return context


class UserOrdersListView(LoginRequiredMixin, ListView):
    """Список заказов выбранного пользователя"""
    model = Order
    template_name = 'shopapp/user_orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        self.owner = get_object_or_404(User, pk=user_id)
        return Order.objects.filter(user=self.owner).prefetch_related('products').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Заказы пользователя: {self.owner.username}'
        context['owner'] = self.owner
        return context


class UserOrdersExportView(LoginRequiredMixin, View):
    """Экспорт заказов пользователя в JSON с кешированием"""

    def get(self, request, user_id):
        # Ключ кэша
        cache_key = f'user_orders_export_{user_id}'

        # Пробуем загрузить из кэша
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return JsonResponse(cached_data, safe=False)

        # Данных нет в кэше — загружаем из БД
        owner = get_object_or_404(User, pk=user_id)
        orders = Order.objects.filter(user=owner).prefetch_related('products').order_by('pk')
        serializer = OrderSerializer(orders, many=True)

        # Сохраняем в кэш на 5 минут
        cache.set(cache_key, serializer.data, 300)

        return JsonResponse(serializer.data, safe=False)