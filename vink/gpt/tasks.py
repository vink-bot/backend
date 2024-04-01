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
def communicate_gpt(chat_token, message):
    """."""
    from .models import Message, Token

    with transaction.atomic():
        message = send_message_gpt(message)
        Message.objects.create(
            message=message,
            token=Token.objects.filter(chat_token=chat_token).first(),
            status=0,
            user="GPT",
        )
