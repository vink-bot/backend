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
        text_responce (str): Сообщение пользователя из чата.
        text_request (str): Сообщение пользователю из чата.
        date_responce (str): Время и дата сообщения (запроса) пользователя.
        date_responce (str): Время и дата сообщения (ответа) пользователю.
        author (class Token): FK анонимного пользователя.
    """

    text_responce = models.TextField()
    text_request = models.TextField(blank=True, null=True)
    date_responce = models.DateTimeField()
    date_request = models.DateTimeField(blank=True, null=True)
    author = models.ForeignKey(
        Token, on_delete=models.CASCADE, related_name="messages"
    )
