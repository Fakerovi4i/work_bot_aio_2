import aiohttp
import logging

from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import bot, MISTRAL_API_URL, session
from config import API_MODEL, API_KEY
from keyboards import ai_keyboard, keyboard_start

logger = logging.getLogger(__name__)

# ================= НАСТРОЙКИ КОНТЕКСТА =================
MAX_HISTORY_LENGTH = 20
SYSTEM_PROMPT = "Ты дружелюбный и полезный помощник в телеграм-боте, тебя зовут Алёнушка. Отвечай кратко и по делу."


async def ai_exit(callback: types.CallbackQuery, state: FSMContext):
    """Выход из режима ИИ + очистка истории"""
    try:
        await bot.answer_callback_query(callback.id)
        await state.finish()
        logger.info(f"Выход из AI режима для пользователя {callback.from_user.id}")
        await bot.send_message(
            callback.from_user.id,
            "Выход из AI режима ⏏️\nИстория очищена 🧹",
            reply_markup=keyboard_start
        )
    except Exception as e:
        logger.exception(f"Ошибка при выходе из AI режима: {e}")

async def chat_with_ai(message: types.Message, state: FSMContext):
    """Главный обработчик чата с контекстом"""
    logger.info(f"Начало обработки сообщения от пользователя {message.from_user.id}")
    # 1. Получаем текущую историю (или создаём новую)
    try:
        async with state.proxy() as data:
            if 'history' not in data:
                data['history'] = [
                    {"role": "system", "content": SYSTEM_PROMPT}
                ]
            history = data['history']

        # 2. Добавляем новое сообщение пользователя
            history.append({"role": "user", "content": message.text})

        # 3. Проверяем лимит контекста
            if len(history) > MAX_HISTORY_LENGTH:
                history = [{"role": "system", "content": SYSTEM_PROMPT}]
                logger.info(f"Достигнут лимит контекста пользователя {message.from_user.id}.")
                await bot.send_message(
                    message.chat.id,
                    "🧹 Достигнут лимит контекста чата.\n"
                    "Начинаю **новый чат ☝️**",
                    parse_mode="HTML"
                )

        payload = {
            "model": API_MODEL,
            "messages": history,  # ← Вот здесь мы и используем наш список словарей!
            "max_tokens": 1024,
            "temperature": 0.7
        }

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        # 4. Делаем запрос к Mistral

        logger.info(f"Отправка запроса к AI от пользователя {message.from_user.id}")
        await bot.send_chat_action(message.chat.id, "typing")

        async with session.post(MISTRAL_API_URL, json=payload, headers=headers) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise Exception(f"HTTP {resp.status}: {text}")
            result = await resp.json()
            ai_answer_text = result['choices'][0]['message']['content']

        # 4. Добавляем ответ в историю и сохраняем
        history.append({"role": "assistant", "content": ai_answer_text})
        async with state.proxy() as data:
            data['history'] = history

        # 5. Отправляем ответ пользователю
        await bot.send_message(
            message.chat.id,
            ai_answer_text,
            reply_markup=ai_keyboard
        )
        logger.info(f"Ответ от AI отправлен пользователю {message.from_user.id}")

    except (aiohttp.ClientError, aiohttp.ClientResponseError) as e:
        logger.error(f"Ошибка при обращении к AI от пользователя {message.from_user.id}: {e}")
        await bot.send_message(
            message.chat.id,
            f"Небольшое прерывание ИИ 😴\n\n"
        )

    except Exception as e:
        logger.exception(f"Непредвиденная ошибка при обращении к AI от пользователя {message.from_user.id}: {e}")
        await bot.send_message(
            message.chat.id,
            f"Ошибка при обращении к AI: {e}",
            reply_markup=ai_keyboard
        )



