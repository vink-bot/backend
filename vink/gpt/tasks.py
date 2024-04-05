import datetime
import time

from celery import shared_task
from celery_singleton import Singleton
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.db.models import F

from .utils import send_message_gpt


@shared_task()
def communicate_gpt(chat_token, message, message_id):
    """."""
    from .models import Message, Token

    with transaction.atomic():
        message = send_message_gpt(message)
        if is_gpt_message_correct(message):
            Message.objects.create(
                message=message,
                token=Token.objects.filter(chat_token=chat_token).first(),
                status=0,
                user="GPT",
            )
        else:
            client_last_message = Message.objects.get(pk=message_id)
            client_last_message.is_handled = False
            client_last_message.recipient = 'OPERATOR'
            client_last_message.save()


def is_gpt_message_correct(message: str) -> bool:
    """Проверка сообщения от GPT на необходимость
    переключения на оператора.
    Если если сообщение корректно возвращает True,
    если нет и нужно переключить на оператора - False."""

    # Здесь можно написать логику проверки на корректность.

    return True
