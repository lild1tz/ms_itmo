from fastapi import FastAPI, HTTPException
from app.models import QueryRequest, ResponseModel
from app.utils import (
    is_relevant_to_itmo,
    process_question_options,
    process_search_results,
    generate_llm_response,
    summarize_contents
)
import asyncio

app = FastAPI()

@app.post("/api/request")
async def handle_request(request: QueryRequest) -> ResponseModel:
    # 1. Проверяем релевантность вопроса к ИТМО
    relevant, reason = await is_relevant_to_itmo(request.query)
    if not relevant:
        # Если вопрос не про ИТМО, возвращаем сразу
        return ResponseModel(
            id=request.id,
            answer=None,
            reasoning=reason,
            sources=[]
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
            id=request.id,
            answer=None,  # answer = null
            reasoning=summary,
            sources=sources[:3]
        )

    # 5. Если варианты есть, генерируем обычный ответ через LLM
    response = await generate_llm_response(
        query=processed_query,
        context='\n'.join(context),
        options=options
    )

    return ResponseModel(
        id=request.id,
        answer=response['answer'],
        reasoning=response['reasoning'],
        sources=sources[:2]  # Ограничиваем список источников 2-мя ссылками
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)