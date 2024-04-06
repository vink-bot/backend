from dataclasses import dataclass

from vink.settings import TELEGRAM_BOT_TOKEN
from telegram import Bot


@dataclass
class IncomingMessage:
    """Входящее сообщение.
    Аттрибуты:
        update_id: int
        user_id: int
        user_first_name: str
        user_last_name: str
        user_username: str
        message_text: str = None
        callback_data: str = None
        callback_query_id: str = None
        client_token: str = None
    """

    update_id: int
    user_id: int
    user_first_name: str
    user_last_name: str
    user_username: str
    message_text: str = None
    callback_data: str = None
    callback_query_id: str = None
    client_token: str = None


def send_message_to_operator_via_tg_bot(
    chat_token: str,
    operator_chat_id: int,
    message_text: str,
    reply_markup=None,
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
    except Exception:
        pass
