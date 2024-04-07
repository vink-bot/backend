from django.db import models

from gpt.models import Token
from .constants import CHAT_TOKEN_SLICE_SIZE


class LastUpdate(models.Model):
    """Модель для хранения последнего обработанного идентификатора
    обновлений в телеграмм.

    Attributes:
        update_id (int): последний обработанный идентификатор обновления.

    """

    update_id = models.PositiveBigIntegerField(
        verbose_name="ИД последнего обработанного обновления",
        blank=False,
        null=False,
    )

    class Meta:
        """Настройка модели LastUpdate."""

        verbose_name = "ИД обновлений ТГ"
        verbose_name_plural = "ИД обновлений ТГ"


class Operator(models.Model):
    """Модель оператор - работающего через телеграм.

    Attributes:
        tg_user_id = models.PositiveBigIntegerField(blank=False, null=False)
        first_name = models.CharField(max_length=100, blank=True, null=True)
        last_name = models.CharField(max_length=100, blank=True, null=True)
        username = models.CharField(max_length=100, blank=True, null=True)
        is_enabled = models.BooleanField(default=False)
    """

    tg_user_id = models.PositiveBigIntegerField(
        verbose_name="ИД оператора в телеграм", blank=False, null=False
    )
    first_name = models.CharField(
        verbose_name="Имя", max_length=100, blank=True, null=True
    )
    last_name = models.CharField(
        verbose_name="Фамилия", max_length=100, blank=True, null=True
    )
    username = models.CharField(
        verbose_name="Имя пользователя", max_length=100, blank=True, null=True
    )
    is_enabled = models.BooleanField(
        verbose_name="Подтвержден",
        default=False)

    class Meta:
        """Настройка модели Operator."""
        verbose_name = "Оператор"
        verbose_name_plural = "операторы"

    @property
    def enabled_verbose(self):
        """Строковое представление для статуса подтверждения (is_enabled)."""
        if self.is_enabled:
            return "Подтвержден, работа в боте разрешена."
        return "Не подтвержден, работа в боте не разрешена."

    @property
    def full_name(self):
        """Полное имя оператора."""
        return f"{self.username} {self.first_name} {self.last_name}"

    def __str__(self):
        """Строковое представление оператора."""
        return f"{self.full_name}"


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
        to=Token,
        on_delete=models.CASCADE,
        related_name="invites",
        null=True,
        blank=True,
        verbose_name="Токен пользователя",
    )
    operator = models.ForeignKey(
        to=Operator,
        on_delete=models.CASCADE,
        related_name="invites",
        verbose_name="Оператор",
    )
    date_create = models.DateTimeField(
        verbose_name="Дата регистрации", auto_now_add=True
    )
    is_active = models.BooleanField(verbose_name="Активно", default=False)

    class Meta:
        """Настройка модели Invite."""
        verbose_name = "Приглашение оператора"
        verbose_name_plural = "приглашения операторам"
    
    @property
    def active_verbose(self):
        """Строковое свойство для представления поля is_active."""
        if self.is_active:
            return "Активен"
        return "Отключен"

    
    def __str__(self):
        """Строковое представление модели Invite."""
        return (
            f"{self.operator.full_name} - "
            f"{self.token.chat_token[:CHAT_TOKEN_SLICE_SIZE]}"
        )


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
        to=Token,
        on_delete=models.CASCADE,
        related_name="chats",
        null=True,
        blank=True,
        verbose_name="Токен пользователя",
    )
    operator = models.ForeignKey(
        to=Operator,
        on_delete=models.CASCADE,
        related_name="chats",
        verbose_name="Оператор",
    )
    date_create = models.DateTimeField(
        verbose_name="Дата создания", auto_now_add=True
    )
    is_active = models.BooleanField(verbose_name="Активен", default=False)

    class Meta:
        """Настройка модели OperatorChat."""
        verbose_name = "Чат оператора в ТГ"
        verbose_name_plural = "Чаты операторов в ТГ"

    @property
    def active_verbose(self):
        """Строковое свойство для представления поля is_active."""
        if self.is_active:
            return "Активен"
        return "Отключен"

    @property
    def status_verbose(self):
        """Строковое свойство для представления поля статуса чата."""
        if self.is_active and self.token is not None:
            return "Активен"
        elif self.is_active and self.token is None:
            return "В ожидании клиента"
        elif self.is_active is False and self.token is not None:
            return "Завершен"
        return "Отключен"

    def __str__(self):
        """Строковое представление для модели OperatorChat."""
        return (
            f"{self.operator.full_name} - "
            f"{self.token.chat_token[:CHAT_TOKEN_SLICE_SIZE]} - "
            f"{self.status_verbose}"
        )
