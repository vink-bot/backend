from django.db import models

from vink.gpt.models import Message, Token

class LastUpdate(models.Model):
    """Модель для хранения последнего обработанного идентификатора
    обновлений в телеграмм.
    
    Attributes:
        update_id (int): последний обработанный идентификатор обновления.
    
    """
    update_id = models.PositiveBigIntegerField(blank=False, null=False)


class OperatorChat(models.Model):
    """Модель для хранения чатов пользователь-оператор в телеграм.
    
    Attributes:
        token (str): chat-token пользователя в веб чате
        operator_user_id (int): user_id оператора в телеграмм
        operator_chat_id (int): chat_id оператора в телеграм-боте
        date_create: дата назначения оператора клиенту
        is_active (bool): активный чат - True, закрыт - False
    """
    token = models.ForeignKey(
        Token, on_delete=models.CASCADE, related_name="operators"
    )
    operator_user_id = models.PositiveBigIntegerField(blank=False, null=False)
    operator_chat_id = models.PositiveBigIntegerField(blank=False, null=False)
    date_create = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)


class ActiveOperator(models.Model):
    """Модель для активных операторов (ожидающих приглашения).
    После окончания работы оператора, запись удаляется.
    
    Attributes:
        operator_user_id (int): user_id оператора в телеграмм
        operator_chat_id (int): chat_id оператора в телеграм-боте
    """
    operator_user_id = models.PositiveBigIntegerField(blank=False, null=False)
    operator_chat_id = models.PositiveBigIntegerField(blank=False, null=False)


class Operator(models.Model):
    """Модель оператор - работающего через телеграм.
    
    Attributes:
        tg_user_id = models.PositiveBigIntegerField(blank=False, null=False)
        first_name = models.CharField(max_length=100, blank=True, null=True)
        last_name = models.CharField(max_length=100, blank=True, null=True)
        username = models.CharField(max_length=100, blank=True, null=True)
        is_enabled = models.BooleanField(default=False)
    """
    tg_user_id = models.PositiveBigIntegerField(blank=False, null=False)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    is_enabled = models.BooleanField(default=False)

