# shopapp/middleware.py

from django.http import HttpResponse
from django.core.cache import cache
from django.conf import settings
import time


class ThrottlingMiddleware:
    """
    Middleware для ограничения частоты запросов от пользователя.
    Если пользователь делает больше MAX_REQUESTS запросов за TIME_WINDOW секунд,
    то ему возвращается ошибка 429 (Too Many Requests).
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Настройки по умолчанию
        self.max_requests = getattr(settings, 'THROTTLE_MAX_REQUESTS', 10)
        self.time_window = getattr(settings, 'THROTTLE_TIME_WINDOW', 60)

    def __call__(self, request):
        # Получаем IP-адрес пользователя
        ip_address = self.get_client_ip(request)

        # Проверяем, не превышен ли лимит запросов
        if self.is_throttled(ip_address):
            return HttpResponse(
                '<h1>429 Too Many Requests</h1>'
                '<p>Вы превысили лимит запросов. Пожалуйста, подождите и попробуйте снова.</p>',
                status=429
            )

        # Обновляем счетчик запросов
        self.update_request_count(ip_address)

        # Продолжаем обработку запроса
        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        """Получает IP-адрес клиента из запроса"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        return ip

    def is_throttled(self, ip_address):
        """Проверяет, превышен ли лимит запросов для данного IP"""
        cache_key = f'throttle_{ip_address}'
        request_data = cache.get(cache_key)

        if request_data is None:
            return False

        current_time = time.time()
        request_count = request_data.get('count', 0)
        first_request_time = request_data.get('first_request_time', current_time)

        # Проверяем, не истекло ли временное окно
        if current_time - first_request_time > self.time_window:
            # Окно истекло, сбрасываем счетчик
            return False

        # Проверяем количество запросов
        if request_count >= self.max_requests:
            return True

        return False

    def update_request_count(self, ip_address):
        """Обновляет счетчик запросов для IP-адреса"""
        cache_key = f'throttle_{ip_address}'
        request_data = cache.get(cache_key)
        current_time = time.time()

        if request_data is None or current_time - request_data.get('first_request_time', 0) > self.time_window:
            # Первый запрос или окно истекло
            request_data = {
                'count': 1,
                'first_request_time': current_time
            }
        else:
            # Увеличиваем счетчик
            request_data['count'] += 1

        # Сохраняем данные в кэш
        cache.set(cache_key, request_data, self.time_window)