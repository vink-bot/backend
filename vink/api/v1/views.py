"""Модуль представлений для приложения API."""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import MessageSerializer
from gpt.models import Message, Token
from gpt.tasks import communicate_gpt
from tg.tg_bot import check_is_in_operator_mode


class SendMessageGPT(APIView):
    """Передать сообщение."""

    def post(self, request):
        headers = request.headers
        chat_token = headers.get("chat-token")
        if not chat_token:
            return Response(
                {"message": "Токен не был передан в заголовках"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        token = Token.objects.filter(chat_token=chat_token).first()
        if not token:
            token = Token.objects.create(chat_token=chat_token)
        data = request.data
        message = data.get("message")
        message_object = Message.objects.create(
            message=message, token=token, status=1, user="USER"
        )

        if not check_is_in_operator_mode(chat_token=chat_token):
            communicate_gpt.delay(chat_token, message, message_object.pk)
        else:
            message_object.recipient = "OPERATOR"
            message_object.is_handled = False
            message_object.save()

        return Response({"message": "Успех"}, status=status.HTTP_201_CREATED)


class ReceiveMessage(APIView):
    """Получить сообщения."""

    def get(self, request):
        headers = request.headers
        chat_token = headers.get("chat-token")
        token = Token.objects.filter(chat_token=chat_token).first()
        messages = Message.objects.filter(token=token, status="0")
        serializer = MessageSerializer(messages, many=True)
        for message in messages:
            message.status = "1"
            message.save()
        return Response(
            {"messages": serializer.data}, status=status.HTTP_200_OK
        )
