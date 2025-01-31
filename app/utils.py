import re
import json
from bs4 import BeautifulSoup
import aiohttp
import ssl
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_openai import ChatOpenAI
from app.config import Config
import asyncio
from typing import Optional, List, Tuple


search = GoogleSerperAPIWrapper(serper_api_key=Config.SERPER_API_KEY)
llm = ChatOpenAI(
    temperature=0,
    openai_api_key=Config.OPENAI_API_KEY,
    base_url=Config.OPENAI_BASE_URL
)


async def fetch_url_content(session: aiohttp.ClientSession, url: str) -> Tuple[str, str]:
    """Функция для получения и парсинга содержимого URL"""
    try:
        # Создаем кастомный SSL-контекст
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        
        async with session.get(url, timeout=10, ssl=ssl_ctx) as response:
            if response.status == 200:
                content_type = response.headers.get('Content-Type', '').lower()
                
                # Проверяем, является ли контент HTML или текстом
                if 'text/html' in content_type or 'text/plain' in content_type:
                    # Получаем кодировку из заголовков ответа, если она указана
                    charset = response.charset if response.charset else 'utf-8'
                    
                    try:
                        # Декодируем текст с использованием указанной кодировки
                        text = await response.text(encoding=charset)
                    except UnicodeDecodeError:
                        # Если возникает ошибка декодирования, пробуем использовать 'latin-1'
                        text = await response.text(encoding='latin-1')
                    
                    return url, text
                
                # Если это не HTML или текст, возвращаем пустую строку
                return url, ""
            else:
                print(f"Failed to retrieve content from {url}, status code: {response.status}")
                return url, ""
    except Exception as e:
        print(f"Error fetching {url}: {str(e)}")
        return url, ""

def parse_content(html: str, word_limit: int = 350) -> str:
    """Функция для парсинга и обрезки содержимого страницы"""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Удаление ненужных элементов
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'form']):
            element.decompose()
        
        # Извлечение текста и ограничение количества слов
        text = ' '.join(soup.stripped_strings)
        words = text.split()
        return ' '.join(words[:word_limit])
    except Exception as e:
        print(f"Error parsing content: {str(e)}")
        return ""

async def is_relevant_to_itmo(question: str) -> Tuple[bool, str]:
    prompt = f"""Проанализируй вопрос и определи его отношение к Университету ИТМО. Ответь строго в JSON:
    {{
        "relevant": boolean,
        "reason": "краткое объяснение на русском языке"
    }}
    Вопрос: {question}"""
    
    try:
        response = await llm.ainvoke(prompt)
        result = json.loads(response.content)
        return result.get('relevant', False), result.get('reason', '')
    except Exception as e:
        return False, f"Ошибка проверки релевантности: {str(e)}"

async def process_question_options(query: str) -> Tuple[str, List[str]]:
    options = re.findall(r'\n\d+\.\s*(.+?)(?=\n\d+\.|\Z)', query, flags=re.DOTALL)
    if len(options) > 10:
        options = options[:10]
        parts = re.split(r'\n\d+\.', query)
        new_query = parts[0] + '\n' + '\n'.join(
            f"{i+1}. {opt.strip()}" for i, opt in enumerate(options)
        )
        return new_query, options
    return query, options

async def generate_llm_response(query: str, context: str, options: List[str]) -> dict:
    answer_instruction = (
        "answer: номер варианта (1-10) или 1, если варианты ответа есть ВСЕГДА ВОЗВРАЩАЙ ЧИСЛО И ТОЛЬКО ЕГО" if options 
        else "answer: всегда null"
    )
    
    prompt = f"""Отвечай строго в JSON. Вопрос: {query}
    Контекст: {context}
    Требования:
    - {answer_instruction}
    - reasoning: краткое обоснование на русском
    - если варианты ответа есть, ВСЕГДА возвращай число в поле answer
    - если информации недостаточно, выбери наиболее вероятный вариант
    """
    
    try:
        response = await llm.ainvoke(prompt)
        result = json.loads(response.content)
        if options:
            answer = result.get('answer')
            if answer is None:
                answer = 1
            else:
                answer = max(1, min(int(answer), len(options)))
        else:
            answer = None
        return {
            "answer": answer,
            "reasoning": result.get('reasoning', 'Обоснование отсутствует'),
            "sources": []
        }
    except Exception as e:
        return {
            "answer": 1 if options else None,
            "reasoning": f"Ошибка генерации ответа: {str(e)}",
            "sources": []
        }

async def process_search_results(question: str) -> Tuple[List[str], List[str]]:
    """Обработка результатов поиска с парсингом контента"""
    try:
        search_results = await asyncio.to_thread(search.results, question)
        organic_results = search_results.get('organic', [])[:3]
        
        async with aiohttp.ClientSession() as session:
            tasks = [fetch_url_content(session, res['link']) for res in organic_results if 'link' in res]
            results = await asyncio.gather(*tasks)
            
            parsed_contents = []
            sources = []
            for url, html in results:
                if html:
                    content = parse_content(html)
                    if content:
                        parsed_contents.append(content)
                        sources.append(url)
                        
            return parsed_contents, sources
    except Exception as e:
        print(f"Search error: {str(e)}")
        return [], []