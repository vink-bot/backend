import datetime

from rest_framework import authentication, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import MessageSerializer
from gpt.models import Message, Token, LastUpdate, OperatorChat, ActiveOperator
from gpt.tasks import communicate_gpt, get_and_process_tg_updates
from gpt.utils import send_message_gpt
from gpt.tg_utils import send_message_to_operator_via_tg_bot, send_notification_to_operators



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


class SendMessageToOperator(APIView):
    """Отправить сообщение оператору."""
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
            message=message, token=token, status=0, user="USER"
        )
        ActiveOperator.objects.create(operator_user_id=5176979730, operator_chat_id=5176979730)
        # Если есть назначенный оператор
        if OperatorChat.objects.filter(token=token, is_active=True).exists():
            operator_chat_id = (
                OperatorChat.objects.filter(
                    token=token, is_active=True
                ).first().operator_chat_id
            )
            # Для теста ставлю свой operator_chat_id = 5176979730
            send_message_to_operator_via_tg_bot(
                chat_token=chat_token,
                operator_chat_id=operator_chat_id,
                message_text=message,
            )
            message_object.status = '1' # Статус отправлено оператору
            message_object.save()
        else:  # Нет назначенного оператора, приглашаем оператора
            operators_chats = list()
            query_set = ActiveOperator.objects.all()
            for item in query_set:
                operators_chats.append(item.operator_chat_id)
            send_notification_to_operators(
                chat_token=chat_token,
                operators_chats=operators_chats
            )
        get_and_process_tg_updates.delay()

        return Response({"message": "Успех"}, status=status.HTTP_201_CREATED)
