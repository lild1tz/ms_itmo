from pydantic import BaseModel
from typing import Optional, List

class QueryRequest(BaseModel):
    query: str
    id: int

class ResponseModel(BaseModel):
    id: int
    answer: Optional[int]
    reasoning: str
    sources: List[str]