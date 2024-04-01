from rest_framework import serializers

from gpt.models import Message


class MessageSerializer(serializers.ModelSerializer):
    """."""

    class Meta:
        model = Message
        fields = ("message", "date_create", "user")
