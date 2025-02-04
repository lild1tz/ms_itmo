# MS ITMO 2025 - FastAPI приложение для обработки запросов ИТМО

[![Python](https://img.shields.io/badge/python-3.11.6-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.75.0-red)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-lagchain-orange)](https://python.langchain.com/)
[![LangChain OpenAI](https://img.shields.io/badge/LangChain-OpenAI-yellow)](https://python.langchain.com/en/latest/modules/llms/integrations/openai.html)
[![License](https://img.shields.io/badge/license-MIT-green)](https://opensource.org/licenses/MIT)

## Описание проекта

MS_ITMO — это FastAPI приложение, предназначенное для обработки запросов, связанных с Университетом ИТМО. Приложение использует машинное обучение для анализа текста и предоставления релевантных ответов на вопросы пользователей. Оно способно различать релевантные и нерелевантные вопросы, а также суммировать контент из найденных источников.

### Возможности

- **Релевантность вопросов**: Проверяет, относится ли вопрос к Университету ИТМО или общей университетской тематике.
- **Обработка вариантов ответов**: Если вопрос содержит варианты ответов, приложение выбирает правильный вариант.
- **Суммаризация текста**: Если вопрос не содержит вариантов ответов, приложение суммирует найденный контент.
- **Асинхронная обработка**: Используется асинхронная обработка HTTP-запросов и парсинга контента для повышения производительности.

### Структура проекта
```
MS_ITMO/
├── .env
├── .gitignore
├── .dockerignore
├── docker-compose.yml
├── Dockerfile
├── README.md
├── requirements.txt
├── venv/
└── app/
    ├── __init__.py
    ├── main.py
    ├── models.py
    ├── utils.py
    └── config.py
```

### Запуск проекта локально

#### 1. Клонирование репозитория

```sh
git clone https://github.com/lild1tz/ms_itmo.git
cd ms_itmo
python -m venv venv
source venv/bin/activate  # Для macOS/Linux
#      venv\Scripts\activate  # Для Windows
```
#### 2. Установка зависимостей
```sh
pip install -r requirements.txt
```

#### 3. Настройка переменных окружения
Создайте файл .env в корне проекта и добавьте следующие переменные:
```sh
SERPER_API_KEY="your_serper_api_key"
OPENAI_API_KEY="your_openai_api_key"
OPENAI_BASE_URL="your_proxy_url"
```

#### 4.1 Запуск сервера (без Докера)
```sh
uvicorn app.main:app --reload
```
Приложение будет доступно по адресу ```http://127.0.0.1:8000```

#### 4.2 Запустить с помощью Docker Compose
```sh
docker-compose up --build
```
Приложение будет доступно по адресу ```http://127.0.0.1:8000```

## Ссылка для внешнего взаимодействия:
```sh
http://77.73.238.26:8000/api/request
```

### Пример использования
Вы можете использовать ```curl``` для отправки запросов к API:
```sh
curl -X POST "http://77.73.238.26:8000/api/request" -H "Content-Type: application/json" -d '{
    "query": "Какие перспективные научные направления сейчас развиваются в ИТМО по квантовым технологиям?\n1. Исследования в области искусственного интеллекта.\n2. Разработка новых материалов для квантовых компьютеров.\n3. Изучение биологических систем.\n4. Моделирование климатических изменений.\n5. Разработка новых алгоритмов для машинного обучения.\n6. Исследование космического пространства.\n7. Создание новых медицинских препаратов.\n8. Развитие технологии блокчейн.\n9. Анализ больших данных.\n10. Исследование генетических структур.",
    "id": 1
}'
```

### Ожидаемый ответ
```json
{
  "id": 1,
  "answer": 2,
  "reasoning": "Краткое обоснование",
  "sources": ["https://...","https://..."]
}
```
