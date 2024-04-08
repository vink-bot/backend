from django.db import models


class Token(models.Model):
    """Модель для распознования анонимного пользователя в чате по токену.
    При появлении в чате пользователя
    ему на frontend'е присваивается Токен.
    """

    chat_token = models.CharField(
        verbose_name="Токен чата пользователя",
        max_length=100,
        unique=True,
    )

    class Meta:
        verbose_name = "Токен чата пользователя"
        verbose_name_plural = "Токены чатов пользователей"


class Message(models.Model):
    """
    Модель для сохранения в БД всей переписки из чата.
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

    message = models.TextField(
        verbose_name="Текст сообщения", blank=True, null=True
    )
    date_create = models.DateTimeField(
        verbose_name="Дата создания", auto_now_add=True
    )
    token = models.ForeignKey(
        to=Token,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="Токен пользователя",
    )
    status = models.CharField(
        verbose_name="Статус", choices=STATUS_TYPES, max_length=15
    )
    user = models.CharField(
        verbose_name="Отправитель", choices=USER_TYPES, max_length=15
    )
    recipient = models.CharField(
        verbose_name="Получатель",
        choices=USER_TYPES,
        max_length=15,
        default="GPT",
    )
    is_handled = models.BooleanField(
        default=True,
        verbose_name="Обработано ТГ-ботом",
    )
    telegram_number_chat = models.PositiveBigIntegerField(
        verbose_name="ИД оператора в телеграмм",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

    def __str__(self):
        chat_token = ""
        if self.token is not None:
            chat_token = self.token.chat_token
        return f"{self.date_create} от {chat_token}: {self.message}"
