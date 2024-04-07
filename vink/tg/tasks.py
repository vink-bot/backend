"""Модуль для задачи Celery-Beat запускающей телеграм бота по расписанию."""

from celery.utils.log import get_task_logger
from vink.celery import app


logger = get_task_logger(__name__)


@app.task(name='tasks.get_and_process_tg_updates')
def get_and_process_tg_updates():
    """Получить и обработать сообщения с телеграмм."""
    from vink.settings import TELEGRAM_BOT_TOKEN
    from .tg_bot import VinkTgBotGetter

    bot = VinkTgBotGetter(TELEGRAM_BOT_TOKEN, logger)
    bot.run()
