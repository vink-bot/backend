"""Модуль задач приложения GPT."""

from celery import shared_task
from django.conf import settings
from django.db import transaction

from .utils import send_message_gpt


@shared_task()
def communicate_gpt(chat_token, message, message_id):
    """Задача отправки сообщений в GPT и получение ответа."""
    from .models import Message, Token

    with transaction.atomic():
        message = send_message_gpt(message)
        if is_gpt_message_correct(message):
            Message.objects.create(
                message=message,
                token=Token.objects.filter(chat_token=chat_token).first(),
                status=0,
                user="GPT",
                recipient="USER",
            )
        else:
            client_last_message = Message.objects.get(pk=message_id)
            client_last_message.is_handled = False
            client_last_message.recipient = "OPERATOR"
            client_last_message.save()


def is_gpt_message_correct(message: str) -> bool:
    """
    Проверяет корректность сообщения от GPT для продолжения общения с ним.
    True - продолжаем общение с GPT.
    False - переводим ответ на оператора.
    """

    return not any(fail in message for fail in settings.GPT_RESPONSE_INCORRECT)
