from fastapi import FastAPI, HTTPException
from app.models import QueryRequest, ResponseModel
from app.utils import (
    is_relevant_to_itmo,  # Функция для проверки релевантности запроса к ИТМО
    process_question_options,  # Функция для обработки вопроса и получения вариантов ответов
    process_search_results,  # Функция для получения контента из первых трех ссылок
    generate_llm_response,  # Функция для генерации ответа с использованием LLM
    summarize_contents  # Функция для суммаризации контента
)
import asyncio

# Создание экземпляра FastAPI
app = FastAPI()

# Декоратор для обработки POST-запросов на эндпоинт /api/request
@app.post("/api/request")
async def handle_request(request: QueryRequest) -> ResponseModel:
    # 1. Проверяем релевантность вопроса к ИТМО
    relevant, reason = await is_relevant_to_itmo(request.query)
    if not relevant:
        # Если вопрос не про ИТМО, возвращаем сразу
        return ResponseModel(
            id=request.id,  # Идентификатор запроса
            answer=None,  # Ответ отсутствует
            reasoning=reason,  # Причина, почему вопрос не релевантен
            sources=[]  # Список источников пустой
        )
    
    # 2. Ищем варианты ответа в тексте
    processed_query, options = await process_question_options(request.query)
    
    # 3. Получаем контент с первых трёх ссылок
    context, sources = await process_search_results(processed_query)
    
    # 4. Обрабатываем случай, когда релевантен, но нет вариантов ответа
    if len(options) == 0:
        # Возвращаем суммаризацию по 3-м ссылкам
        summary = await summarize_contents(context)
        return ResponseModel(
            id=request.id,  # Идентификатор запроса
            answer=None,  # Ответ отсутствует
            reasoning=summary,  # Суммаризация контента
            sources=sources[:3]  # Первые три источника
        )
    
    # 5. Если варианты есть, генерируем обычный ответ через LLM
    response = await generate_llm_response(
        query=processed_query,  # Обработанный запрос
        context='\n'.join(context),  # Контент из первых трех ссылок
        options=options  # Варианты ответов
    )
    
    return ResponseModel(
        id=request.id,  # Идентификатор запроса
        answer=response['answer'],  # Генерированный ответ
        reasoning=response['reasoning'],  # Причина выбора ответа
        sources=sources[:3]  # Первые три источника
    )

if __name__ == "__main__":
    import uvicorn
    # Запуск сервера FastAPI
    uvicorn.run(app, host="0.0.0.0", port=8000)