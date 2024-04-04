from dataclasses import dataclass

from vink.settings import TELEGRAM_BOT_TOKEN
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup




@dataclass
class IncomingMessage:
    """Входящее сообщение.
    
    Аттрибуты:
        update_id: int
        chat_id: int
        user_id: int
        message_text: str = None
        callback_data: str = None
        callback_query_id: str = None
        client_token: str = None
    """
    update_id: int
    chat_id: int
    user_id: int
    user_first_name: str
    user_last_name: str
    user_username: str
    message_text: str = None
    callback_data: str = None
    callback_query_id: str = None
    client_token: str = None
    


def send_message_to_operator_via_tg_bot(
        chat_token: str, operator_chat_id: int, message_text: str,
        reply_markup=None
):
    """Отправляет сообщения от клиента оператору через чат бот телеграмм."""
    TG_BOT: Bot = Bot(TELEGRAM_BOT_TOKEN)
    try:
        TG_BOT.send_message(
            chat_id=operator_chat_id,
            text=message_text,
            reply_markup=reply_markup,
        )
        # logger.debug(f'Чат-бот удачно отправил сообщение: {message}.')
    except Exception as exception:
        error_message = f'Чат-бот не смог отправить сообщение: {message_text}. {exception}'
        # self.logger.error(error_message)
    pass


def send_notification_to_operators(
        chat_token: str,
        operators_chats: list
):
    button = InlineKeyboardButton(
        text='Начать переписку с клиентом',
        callback_data=chat_token)
    reply_markup = InlineKeyboardMarkup([[button]])
    for chat_id in operators_chats:
        send_message_to_operator_via_tg_bot(
            chat_token=chat_token,
            operator_chat_id=chat_id,
            reply_markup=reply_markup,
            message_text=f'Есть новое сообщение от клиента {chat_token}.'
        )
