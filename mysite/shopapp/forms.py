# shopapp/forms.py

from django import forms
from .models import Product, Order


class FileUploadForm(forms.Form):
    file = forms.FileField(
        label='Выберите файл',
        help_text='Максимальный размер файла: 1 МБ'
    )
    description = forms.CharField(
        max_length=200,
        required=False,
        label='Описание файла',
        widget=forms.TextInput(attrs={'placeholder': 'Введите описание файла'})
    )


class ProductForm(forms.ModelForm):
    """
    Форма для создания продукта на основе модели Product
    """
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'discount', 'quantity', 'in_stock', 'category']
        labels = {
            'name': 'Название товара',
            'description': 'Описание товара',
            'price': 'Цена (руб.)',
            'discount': 'Скидка (%)',
            'quantity': 'Количество на складе',
            'in_stock': 'В наличии',
            'category': 'Категория',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название товара'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Введите описание товара'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00'
            }),
            'discount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
        }


class OrderForm(forms.ModelForm):
    """
    Форма для создания заказа на основе модели Order
    """
    class Meta:
        model = Order
        fields = ['delivery_address', 'promocode', 'user', 'products']
        labels = {
            'delivery_address': 'Адрес доставки',
            'promocode': 'Промокод',
            'user': 'Пользователь',
            'products': 'Товары',
        }
        widgets = {
            'delivery_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Введите адрес доставки'
            }),
            'promocode': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите промокод (необязательно)'
            }),
            'user': forms.Select(attrs={
                'class': 'form-control'
            }),
            'products': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
        }


class CSVImportForm(forms.Form):
    csv_file = forms.FileField(label='CSV файл')