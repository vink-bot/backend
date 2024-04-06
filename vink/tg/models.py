from django.db import models

from gpt.models import Token


class LastUpdate(models.Model):
    """Модель для хранения последнего обработанного идентификатора
    обновлений в телеграмм.

    Attributes:
        update_id (int): последний обработанный идентификатор обновления.

    """

    update_id = models.PositiveBigIntegerField(blank=False, null=False)


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


class Invite(models.Model):
    """Модель приглашений операторам о новых вопросах клиентов.

    Attributes:
        token = models.ForeignKey(
            Token, on_delete=models.CASCADE, related_name="invites"
        )
        operator = models.ForeignKey(
            Operator, on_delete=models.CASCADE, related_name="invites"
        )
        date_create = models.DateTimeField(auto_now_add=True)
        is_active = models.BooleanField(default=False)
    """

    token = models.ForeignKey(
        Token,
        on_delete=models.CASCADE,
        related_name="invites",
        null=True,
        blank=True,
    )
    operator = models.ForeignKey(
        Operator, on_delete=models.CASCADE, related_name="invites"
    )
    date_create = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)


class OperatorChat(models.Model):
    """Модель для хранения чатов пользователь-оператор в телеграм.

    Attributes:
        token models.ForeignKey(
            Token, on_delete=models.CASCADE, related_name="operators)
        operator_user_id (int): user_id оператора в телеграмм
        date_create: дата назначения оператора клиенту
        is_active (bool): активный чат - True, закрыт - False
    """

    token = models.ForeignKey(
        Token,
        on_delete=models.CASCADE,
        related_name="chats",
        null=True,
        blank=True,
    )
    operator = models.ForeignKey(
        Operator, on_delete=models.CASCADE, related_name="chats"
    )
    date_create = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
