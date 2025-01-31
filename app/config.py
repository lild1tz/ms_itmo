from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    SERPER_API_KEY = os.getenv('SERPER_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL')