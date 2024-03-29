import datetime

from rest_framework import authentication, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

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
        text_responce = data.get("message")
        date_responce = data.get("date")
        message = Message.objects.create(
            text_responce=text_responce,
            date_responce=date_responce,
            author=token,
        )

        communicate_gpt.delay(message.id)

        return Response({"message": "Успех"}, status=status.HTTP_201_CREATED)
