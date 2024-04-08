from rest_framework import serializers

from gpt.models import Message


class MessageSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Message."""

    class Meta:
        model = Message
        fields = ("message", "date_create", "user")
