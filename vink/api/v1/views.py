import datetime

from rest_framework import authentication, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import MessageSerializer
from gpt.models import Message, Token
from gpt.tasks import communicate_gpt
from gpt.utils import send_message_gpt


class SendMessageGPT(APIView):
    """."""

    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAdminUser]

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
        Message.objects.create(
            message=message, token=token, status=1, user="USER"
        )

        communicate_gpt.delay(chat_token, message)

        return Response({"message": "Успех"}, status=status.HTTP_201_CREATED)


class ReceiveMessage(APIView):
    """."""

    def get(self, request):
        headers = request.headers
        chat_token = headers.get("chat-token")
        token = Token.objects.filter(chat_token=chat_token).first()
        messages = token.messages.filter(status="0")
        serializer = MessageSerializer(messages, many=True)
        for message in messages:
            message.status = "1"
            message.save()
        return Response(
            {"messages": serializer.data}, status=status.HTTP_200_OK
        )
