from fastapi import FastAPI, HTTPException
from app.models import QueryRequest, ResponseModel
from app.utils import (
    is_relevant_to_itmo, process_question_options, process_search_results,
    generate_llm_response
)
import asyncio

app = FastAPI()

@app.post("/api/request")
async def handle_request(request: QueryRequest) -> ResponseModel:
    relevant, reason = await is_relevant_to_itmo(request.query)
    if not relevant:
        return ResponseModel(
            id=request.id,
            answer=None,
            reasoning=reason,
            sources=[]
        )
    
    processed_query, options = await process_question_options(request.query)
    context, sources = await process_search_results(processed_query)
    response = await generate_llm_response(
        query=processed_query,
        context='\n'.join(context),
        options=options
    )
    
    return ResponseModel(
        id=request.id,
        answer=response['answer'],
        reasoning=response['reasoning'],
        sources=sources[:2]
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)