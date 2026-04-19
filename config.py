import os
from dotenv import load_dotenv, find_dotenv


if not find_dotenv():
    exit("Переменные окружения не загружены, так как отсутствует файл .env")
else:
    load_dotenv()

TOKEN = os.getenv('TOKEN')
API_KEY = os.getenv('API_KEY')
API_MODEL = os.getenv('API_MODEL')


API_TIMEOUT = 30