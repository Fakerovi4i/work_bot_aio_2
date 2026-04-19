from aiogram import executor
from aiogram.dispatcher.filters import Text

from loader import dp, schedule, session
from database import db

from handlers.ai_handlers import ai_exit, chat_with_ai
from handlers.user_handlers import (start, start_keyboard, user_send_doc,
                                    user_send_message, inwork_function, delete_task)

from handlers.admin_handlers import (
    admin, admin_choose_option, admin_want_choose_ban, admin_want_choose_unban, admin_nameTask_insert,
    admin_desriptionTask_insert, admin_imgTask_insert, admin_choose_user, admin_send_allmessage,
    admin_send_one_message, admin_send_onecall, delete_back_look, delete_doc,
    admin_break_task, continue_without_photo, admin_add, admin_add_callback, admin_dell, admin_dell_callback)

from states_group import (AdminInsertTasks, AdminAllMessage, AdminOneMessage,
                          UserSendSome, UserSendDoc, UserChatWithAI)

from utils import schedul
import logging
from logging_config import setup_logging

logger = logging.getLogger(__name__)




async def on_startup(_):
    """Запуск бота"""
    logger.info("🤖 Бот Успешно Запущен 🚀")
    db.create_tables()

    schedul()
    schedule.start()
    logger.info("База данных подключена, планировщик запущен")

async def on_shutdown(dispatcher):
    """Корректное завершение работы бота"""
    logger.info("🤖 Бот Закрывается...")

    if schedule.running:
        schedule.shutdown(wait=True)
        logger.info("Планировщик остановлен.")

    if session and not session.closed:
        await session.close()
        logger.info("Сессия aiohttp закрыта.")

    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()
    logger.info("FSM хранилище закрыто.")
    logger.info("🤖 Бот успешно остановлен 🚀")


if __name__ == '__main__':
    setup_logging()
    # logging.getLogger('aiogram.dispatcher.dispatcher').setLevel(logging.WARNING)
    logger = logging.getLogger(__name__)
    logger.info("🤖 Бот запускается...")


    # Регистрация всех Message-обработчиков
    dp.register_message_handler(start, commands='start', state=None)
    dp.register_message_handler(admin, commands='admin', state=None)
    dp.register_message_handler(admin_add, commands='addadmin', state=None)
    dp.register_message_handler(admin_dell, commands='delladmin', state=None)

    # User handlers
    dp.register_message_handler(user_send_message, content_types='text', state=UserSendSome.msg)
    dp.register_message_handler(user_send_doc, content_types='text', state=UserSendDoc.doc)

    # Admin handlers
    dp.register_message_handler(admin_nameTask_insert, content_types='text', state=AdminInsertTasks.name)
    dp.register_message_handler(admin_desriptionTask_insert, content_types='text', state=AdminInsertTasks.description)
    dp.register_message_handler(admin_imgTask_insert, content_types=['photo', 'text'], state=AdminInsertTasks.img)
    dp.register_message_handler(admin_choose_user, content_types='text', state=AdminInsertTasks.callback)

    dp.register_message_handler(admin_send_allmessage, content_types='text', state=AdminAllMessage.msg)
    dp.register_message_handler(admin_send_one_message, content_types='text', state=AdminOneMessage.msg)
    dp.register_message_handler(admin_send_onecall, content_types='text', state=AdminOneMessage.call)



    # AI handler
    dp.register_message_handler(chat_with_ai, content_types='text', state=UserChatWithAI.chatting)

    # Callback-обработчики
    dp.register_callback_query_handler(start_keyboard, Text(startswith='start_'), state=None)
    dp.register_callback_query_handler(inwork_function, Text(startswith='inwork_'), state=None)
    dp.register_callback_query_handler(admin_choose_option, Text(startswith='admin_'), state=None)
    dp.register_callback_query_handler(admin_add_callback, Text(startswith='addadmin_'), state=None)
    dp.register_callback_query_handler(admin_dell_callback, Text(startswith='delladmin_'), state=None)
    dp.register_callback_query_handler(delete_back_look, Text(startswith='deletelook_'), state=None)
    dp.register_callback_query_handler(admin_want_choose_ban, Text(startswith='ban_'), state=None)
    dp.register_callback_query_handler(admin_want_choose_unban, Text(startswith='unban_'), state=None)
    dp.register_callback_query_handler(ai_exit, Text(startswith='ai_'), state=UserChatWithAI.chatting)
    dp.register_callback_query_handler(delete_task, Text(startswith='delete_task_'), state=None)
    dp.register_callback_query_handler(delete_doc, Text(startswith='deletedoc_'), state=None)
    dp.register_callback_query_handler(admin_break_task, Text('admin_break'), state=[AdminInsertTasks.name, AdminInsertTasks.description, AdminInsertTasks.img, AdminInsertTasks.callback, AdminOneMessage.call, AdminOneMessage.msg])
    dp.register_callback_query_handler(continue_without_photo, Text('admin_without_photo'), state=AdminInsertTasks.img)

    # ========== ЗАПУСК ===============
    try:
        executor.start_polling(
            dp,
            skip_updates=True,
            on_startup=on_startup,
            on_shutdown=on_shutdown
        )
    except Exception as e:
        logger.critical(f"🚨 Критическая ошибка: {e}")


