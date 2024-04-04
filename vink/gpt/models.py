from django.db import models


class Token(models.Model):
    """Модель, которая необходима для распознования анонимного пользователя
    в чате по токену. При появлении в чате пользователя ему на frontend'е
    присваивается Токен.

    Attributes:
        chat_token (str): Токен анонимного пользователя в чате.
    """

    chat_token = models.CharField(max_length=100, unique=True)


class Message(models.Model):
    """Модель, которая необходима для сохранения в БД всей переписки из чата.

    Attributes:
        example (str): Бла бла бла.
    """

    STATUS_TYPES = (
        ("0", "0"),
        ("1", "1"),
        ("3", "3"),
    )
    USER_TYPES = (
        ("USER", "USER"),
        ("GPT", "GPT"),
        ("OPERATOR", "OPERATOR"),
    )

    RECEPIENT_TYPES = (
        ("GPT", "GPT"),
        ("OPERATOR", "OPERATOR"),
    )

    message = models.TextField(blank=True, null=True)
    date_create = models.DateTimeField(auto_now_add=True)
    token = models.ForeignKey(
        Token, on_delete=models.CASCADE, related_name="messages"
    )
    status = models.CharField(choices=STATUS_TYPES, max_length=15)
    user = models.CharField(choices=USER_TYPES, max_length=15)
    recepient = models.CharField(
        choices=RECEPIENT_TYPES, max_length=15, default='GPT')
    telegram_number_chat = models.PositiveBigIntegerField(blank=True, null=True)


