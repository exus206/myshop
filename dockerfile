FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

# Установите системные зависимости для Pillow
RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Установите Poetry
RUN pip install poetry

# Копируйте файлы зависимостей
COPY pyproject.toml poetry.lock* /app/

# Установите зависимости без создания виртуального окружения
RUN poetry install --no-root --no-interaction --no-ansi

# Копируйте исходный код
COPY . /app/

# Откройте порт
EXPOSE 8000

# Запустите приложение
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]