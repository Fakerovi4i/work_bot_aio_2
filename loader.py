import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from mistralai.client import Mistral

from config import TOKEN

MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"


# === Исправление "Proxy is closed!" ===
connector = aiohttp.TCPConnector(
    limit=0, # не ограничиваем количество соединений
    ttl_dns_cache=300,
    keepalive_timeout=30
)

session = aiohttp.ClientSession(connector=connector)

# ====================== БОТ ======================
bot = Bot(token=TOKEN, timeout=60)

bot._session = session
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
schedule = AsyncIOScheduler()