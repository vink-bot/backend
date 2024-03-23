from django.db import models


class Token(models.Model):
    """Модель, которая необходима для распознования анонимного пользователя
    в чате по токену. При появлении в чате пользователя ему на frontend'е
    присваивается Токен и передается на backend.

    Attributes:
        token_value (str): Токен анонимного пользователя в чате.
        status (str): Статус диалога (с кем общается пользователь).
    """

    STATUS_TYPES = (
        ("off", "Не в системе"),
        ("gpt", "YandexGPT"),
        ("operator", "Оператор"),
    )
    token_value = models.CharField(max_length=100)
    status = models.CharField(choices=STATUS_TYPES, max_length=15)


class Message(models.Model):
    """Модель, которая необходима для сохранения в БД всей переписки из чата.

    Attributes:
        text_responce (str): Сообщение пользователя из чата.
        text_request (str): Сообщение пользователю из чата.
        date (str): Время и дата ообщения.
        author (class Token): FK анонимного пользователя.
    """

    text_responce = models.TextField()
    text_request = models.TextField(blank=True, null=True)
    date = models.DateTimeField()
    author = models.ForeignKey(
        Token, on_delete=models.CASCADE, related_name="messages"
    )
