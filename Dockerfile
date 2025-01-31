# Используем официальный образ Python 3.11-slim
FROM python:3.11.6-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем только файл requirements.txt для установки зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы проекта
COPY . .

# Экспортируем переменные окружения из файла .env
# Для этого используем библиотеку python-dotenv
RUN pip install python-dotenv

# Команда для запуска приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]