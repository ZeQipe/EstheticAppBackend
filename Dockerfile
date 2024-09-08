FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Здесь мы проверяем подключение к базе данных перед выполнением миграций
CMD ["sh", "-c", "python src/manage.py wait_for_db && python src/manage.py migrate && python src/manage.py runserver 0.0.0.0:8000"]
