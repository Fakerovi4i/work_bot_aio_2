import os
from dotenv import load_dotenv, find_dotenv

# Сделано для развертывания
dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path)
# Локально
# if not find_dotenv():
#     exit("Переменные окружения не загружены, так как отсутствует файл .env")
# else:
#     load_dotenv()

TOKEN = os.getenv('TOKEN')
API_KEY = os.getenv('API_KEY')
API_MODEL = os.getenv('API_MODEL')

API_TIMEOUT = 30