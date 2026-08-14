# shopapp/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import viewsets

app_name = 'shopapp'

# API Router
router = DefaultRouter()
router.register('products', viewsets.ProductViewSet, basename='api_product')
router.register('orders', viewsets.OrderViewSet, basename='api_order')

urlpatterns = [
    # Главная
    path('', views.ShopIndexView.as_view(), name='shop_index'),

    # Продукты
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('products/create/', views.ProductCreateView.as_view(), name='create_product'),
    path('products/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/archive/', views.ProductArchiveView.as_view(), name='product_archive'),
    path('products/latest/feed/', views.LatestProductsFeed(), name='products_feed'),

    # Заказы
    path('orders/', views.OrderListView.as_view(), name='order_list'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('orders/create/', views.OrderCreateView.as_view(), name='create_order'),
    path('orders/<int:pk>/update/', views.OrderUpdateView.as_view(), name='order_update'),
    path('orders/<int:pk>/delete/', views.OrderDeleteView.as_view(), name='order_delete'),
    path('orders/export/', views.OrdersExportView.as_view(), name='orders_export'),
    path('orders/api/export/', views.OrdersExportApiView.as_view(), name='orders_api_export'),
    path('users/<int:user_id>/orders/', views.UserOrdersListView.as_view(), name='user_orders'),
    path('users/<int:user_id>/orders/export/', views.UserOrdersExportView.as_view(), name='user_orders_export'),

    # Файлы
    path('upload/', views.FileUploadView.as_view(), name='upload_file'),
    path('files/', views.FileListView.as_view(), name='file_list'),

    # API
    path('api/', include(router.urls)),
]