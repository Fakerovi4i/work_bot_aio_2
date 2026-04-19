import datetime
import logging

from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import bot
from database import db
from states_group import UserSendSome, UserSendDoc, UserChatWithAI
from keyboards import keyboard_start, inwork_keyboard, ai_keyboard

logger = logging.getLogger(__name__)

# ============ /start ===========
async def start(message: types.Message, state: FSMContext):

    try:
        logger.info(f"Начало работы пользователя {message.from_user.id}")
        user = db.get_user(message.from_user.id)
        if user is None:
            dates = datetime.date.today()
            db.add_user(dates, message.chat.id, message.from_user.username, 0)
            await bot.send_message(message.chat.id,
                f"🖖 Привет! я твой личный помощник.\nЯ помогу тебе в рабочих процессах",
                reply_markup=keyboard_start)
        else:
            ban = db.get_ban(message.chat.id)
            if ban == 1:
                await bot.send_message(message.chat.id, "Админ Вас Забанил")
            else:
                await bot.send_message(message.chat.id,
                    f'🖖 Привет! я твой личный помощник.\n'
                    f'Я помогу тебе в рабочих процессах 🦾',
                    reply_markup=keyboard_start
                )
    except Exception as e:
        logger.exception(f"Ошибка при начале работы пользователя {message.from_user.id}: {e}")

# ============ КНОПКИ СТАРТОВОГО МЕНЮ ===========
async def start_keyboard(callback: types.CallbackQuery, state: FSMContext):
    try:
        await bot.answer_callback_query(callback.id)
        str_data = callback.data.split('_')[1]
        logger.info(f"Пользователь {callback.from_user.id} выбрал команду {str_data}")
        ban = db.get_ban(callback.from_user.id)
        if ban == 1:
            logger.info(f"Пользователь {callback.from_user.id} в бане")
            await bot.send_message(callback.from_user.id, "Админ Вас Забанил ⛔")
            return

        if str_data == 'AI':
            await bot.send_message(
                callback.from_user.id, "Привет! Я Алёнушка, ваш дружелюбный помощник. Чем могу помочь? 😊",
                reply_markup=ai_keyboard
            )
            await UserChatWithAI.chatting.set()

        if str_data == 'info':
            await bot.send_message(
                callback.from_user.id,
                "🦾 <b>Я — твой личный помощник в работе.</b>\n"
                "\nЗдесь ты можешь:\n\n"
                "🪧 Получать задачи от админа\n\n"
                "🚲 Отмечать приход/уход\n\n"
                "📝 Отправлять отчёты\n\n"
                "🤖 Общаться с ИИ\n\n"
                "Если есть вопросы — пиши в «Внести пожелание»",
                parse_mode="HTML",
                reply_markup=keyboard_start
            )

        if str_data == 'tasks':
            tasks = db.get_user_tasks(callback.from_user.id)

            if not tasks:
                await bot.send_message(callback.from_user.id, "📋 <b>У вас нет задач.</b>", parse_mode="HTML")
                return

            for task_id, name, description, photo in tasks:
                keyboard = types.InlineKeyboardMarkup(row_width=1)
                keyboard.add(types.InlineKeyboardButton(
                    text="❌ Удалить задачу",
                    callback_data=f"delete_task_{task_id}"
                ))

                await bot.send_photo(
                    callback.from_user.id,
                    photo,
                    f"<b>{name}</b>\n\n{description}",
                    parse_mode="HTML",
                    reply_markup=keyboard
                )

        if str_data == 'inwork':
            await bot.send_message(callback.from_user.id, f"📯 Выбери", reply_markup=inwork_keyboard)

        if str_data == 'sendsome':
            await bot.send_message(callback.from_user.id, f"Отправь идею или пожелание:")
            await UserSendSome.msg.set()

        if str_data == 'document':
            await bot.send_message(
                callback.from_user.id,
                f"✒️ Отправь отчет который содержит:\n\n")
            await bot.send_message(
                callback.from_user.id,
                f"Количество поставленных задач:\n"
                f"Количество выполненных задач:\n"
                f"Количество затраченных часов:\n"
            )
            await UserSendDoc.doc.set()
    except Exception as e:
        logger.exception(f"Ошибка при выборе команды пользователя {callback.from_user.id}: {e}")

# ====================== ОТПРАВКА ОТЧЁТА (Doc) ======================
async def user_send_doc(message: types.Message, state: FSMContext):
    try:
        logger.info(f"Пользователь {message.from_user.id} отправляет отчет")
        ban = db.get_ban(message.from_user.id)
        if ban == 1:
            await bot.send_message(message.chat.id, f"Вы забанены ⛔")
            return

        async with state.proxy() as data:
            data["datatime"] = datetime.datetime.today()
            data["call"] = message.chat.id
            data["doc"] = message.text
            data["link"] = message.from_user.username
            msg = data["doc"]

        required_phrases = [
            "Количество поставленных задач",
            "Количество выполненных задач",
            "Количество затраченных часов"
        ]

        if all(phrase in msg for phrase in required_phrases):
            db.insert_doc(data["datatime"], data["call"], data["doc"], data["link"])
            await state.finish()
            await bot.send_message(
                message.chat.id,
                f"Документ отправлен",
                reply_markup=keyboard_start
            )
        else:
            await bot.send_message(
                message.chat.id,
                f"Документ не соответствует требованиям!\n\n"
                f"Убедись, что в тексте есть все три пункта:\n"
            )
            await bot.send_message(
                message.chat.id,
                f"Количество поставленных задач:\n"
                f"Количество выполненных задач:\n"
                f"Количество затраченных часов:\n"
            )

            await UserSendDoc.doc.set()
    except Exception as e:
        logger.exception(f"Ошибка при отправке отчета пользователя {message.from_user.id}: {e}")

# ====================== ОТПРАВКА ПОЖЕЛАНИЯ (Improve) ===============
async def user_send_message(message: types.Message, state: FSMContext):
    try:
        logger.info(f"Пользователь {message.from_user.id} отправляет пожелание")
        ban = db.get_ban(message.from_user.id)
        if ban == 1:
            await bot.send_message(message.chat.id, f"Вы забанены")
            return

        async with state.proxy() as data:
            data["datatime"] = datetime.datetime.today()
            data["call"] = message.chat.id
            data["text"] = message.text

        db.insert_improve(data["datatime"], data["call"], data["text"])
        await state.finish()
        await bot.send_message(
            message.chat.id,
            f"Сообщение отправлено 👍",
            reply_markup=keyboard_start
        )
    except Exception as e:
        logger.exception(f"Ошибка при отправке пожелания пользователя {message.from_user.id}: {e}")

# ====================== ОТМЕТКА ПРИХОД/УХОД ======================
async def inwork_function(callback: types.CallbackQuery, state: FSMContext):
    try:
        logger.info(f"Пользователь {callback.from_user.id} делает отметку прихода/ухода")
        await bot.answer_callback_query(callback.id)
        action = callback.data.split('_')[1]

        ban = db.get_ban(callback.from_user.id)
        if ban == 1:
            await bot.send_message(callback.from_user.id, f"Вы забанены")
            return

        date = datetime.datetime.now()
        hour = date.hour
        minute = date.minute

        if action == 'come':
            db.insert_inwork(datetime.date.today(), callback.from_user.id, callback.from_user.username, hour, minute)
            await bot.send_message(
                callback.from_user.id,
                f"Хорошей работы",
                reply_markup=keyboard_start
            )
        elif action == 'out':
            db.insert_outwork(datetime.date.today(), callback.from_user.id, callback.from_user.username, hour, minute)
            await bot.send_message(
                callback.from_user.id,
                f"Хорошего отдыха",
                reply_markup=keyboard_start
            )
    except Exception as e:
        logger.exception(f"Ошибка при отметке прихода/ухода пользователя {callback.from_user.id}: {e}")

# ====================== УДАЛЕНИЕ ЗАДАЧИ =======================
async def delete_task(callback: types.CallbackQuery, state: FSMContext):
    try:
        logger.info(f"Пользователь {callback.from_user.id} удаляет задачу")
        await bot.answer_callback_query(callback.id)
        task_id = int(callback.data.split('_')[2])

        db.delete_task(task_id)
        await bot.send_message(
            callback.from_user.id,
            "✅ Задача успешно удалена",
            reply_markup=keyboard_start
        )
    except Exception as e:
        logger.exception(f"Ошибка при удалении задачи пользователя {callback.from_user.id}: {e}")





