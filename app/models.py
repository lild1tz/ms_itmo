from pydantic import BaseModel
from typing import Optional, List

# Определение модели для запроса
class QueryRequest(BaseModel):
    query: str  # Текстовый запрос пользователя
    id: int  # Уникальный идентификатор запроса

# Определение модели для ответа
class ResponseModel(BaseModel):
    id: int  # Уникальный идентификатор запроса (связь с запросом)
    answer: Optional[int]  # Ответ на запрос (может быть None, если ответ не требуется)
    reasoning: str  # Обоснование или причина, почему выбран данный ответ
    sources: List[str]  # Список источников, используемых для формирования ответа

# Комментарии к каждой строке:

# 1. Импорт базовой модели Pydantic для создания моделей данных
from pydantic import BaseModel

# 2. Импорт типов для указания опциональных полей и списков
from typing import Optional, List

# 3. Определение модели для запроса
class QueryRequest(BaseModel):
    # Поле "query" - это текстовый запрос пользователя
    query: str
    
    # Поле "id" - это уникальный идентификатор запроса, который позволяет связать запрос и ответ
    id: int

# 4. Определение модели для ответа
class ResponseModel(BaseModel):
    # Поле "id" - это уникальный идентификатор запроса, который позволяет связать запрос и ответ
    id: int
    
    # Поле "answer" - это ответ на запрос, может быть опциональным (None, если ответ не требуется)
    answer: Optional[int]
    
    # Поле "reasoning" - это обоснование или причина, почему был выбран данный ответ
    reasoning: str
    
    # Поле "sources" - это список источников, используемых для формирования ответа
    sources: List[str]

# Эти модели используются для валидации входных данных и формирования структурированных ответов в FastAPI-приложении.