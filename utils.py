import datetime
import logging

from loader import bot, schedule
from database import db
from keyboards import inwork_keyboard

logger = logging.getLogger(__name__)

async def welcome_to_job_schedl():
    '''Напоминание отметиться'''
    for call, _ in db.get_active_users():
        try:
            await bot.send_message(
                call,
                "🕒 Не забудь отметиться.",
                reply_markup=inwork_keyboard
            )
        except Exception as e:
            logger.exception(f"Ошибка при отправке сообщения в планировщике: {e}")


async def send_doc_schedl():
    """Напоминание отправить отчёт"""
    for call, _ in db.get_active_users():
        try:
            await bot.send_message(
                call,
                "Не забудь отправить отчет."
            )
        except Exception as e:
            logger.exception(f"Ошибка при отправке сообщения в планировщике: {e}")


async def interval_for_job_schedl():
    """Периодический контроль (каждые 3 часа по рабочим дням)"""
    if datetime.datetime.today().weekday() >= 5:
        return
    for call, _ in db.get_active_users():
        try:
            await bot.send_message(
                call,
                "Слежу за тобой -_-"
            )
        except Exception as e:
            logger.exception(f"Ошибка при отправке сообщения в планировщике: {e}")


def schedul():
    """Регистрация всех задач планировщика"""
    logger.info("Регистрация задач планировщика...")
    schedule.add_job(welcome_to_job_schedl, "cron", day_of_week="mon-fri", hour=8, minute=55)
    schedule.add_job(send_doc_schedl, "cron", day_of_week="fri", hour=14, minute=0)
    schedule.add_job(interval_for_job_schedl, "interval", hours=3)
