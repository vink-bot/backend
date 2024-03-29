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
def communicate_gpt(message_id):
    """."""
    from .models import Message

    with transaction.atomic():
        message = Message.objects.get(id=message_id)
        text_request = send_message_gpt(message.text_responce)
        date_request = datetime.datetime.now()
        message.text_request = text_request
        message.date_request = date_request
        message.save()
