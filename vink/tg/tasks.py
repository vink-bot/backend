from logging import Logger
from celery.utils.log import get_task_logger
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters

from vink.celery import app


logger = get_task_logger(__name__)

@app.task(name='tasks.get_and_process_tg_updates')
def get_and_process_tg_updates():
    """Получить и обработать сообщения с телеграмм."""
    
    from vink.settings import TELEGRAM_BOT_TOKEN
    from .models import Message, LastUpdate, Token
    from .tg_utils import IncomingMessage

    bot = Bot(TELEGRAM_BOT_TOKEN)

    def get_updates() -> list[IncomingMessage]:

        if LastUpdate.objects.exists():
            offset = LastUpdate.objects.first().update_id + 1
        else:
            offset = None

        updates: list[Update] = bot.get_updates(offset=offset)
        print('Bot get updates: ', len(updates), '.')
        result = []
        last_update_id = 0
        for upd in updates:

            callback_data: str = None
            callback_query_id: str = None
            if upd.callback_query:
                # print(upd.callback_query)
                callback_data = upd.callback_query.data
                callback_query_id = upd.callback_query.id
            incoming_message = IncomingMessage(
                update_id=upd.update_id,
                chat_id=upd.effective_chat.id,
                user_id=upd.effective_user.id,
                message_text=upd.effective_message.text,
                callback_data=callback_data,
                callback_query_id=callback_query_id
            )
            last_update_id = upd.update_id
            
            result.append(incoming_message)
        if offset:
            LastUpdate.objects.first().update_id = last_update_id
        else:
            LastUpdate.objects.create(update_id=last_update_id)
        
        return result
    
    def parse_incoming_message(incoming_message_list: list[IncomingMessage]):
        """ Разбор списка сообщений."""
        for message in incoming_message_list:
            print(message)
            if message.message_text == '/start':
                start_waiting_handler(message)
            elif message.message_text == '/finish':
                finish_working_handler(message)
            elif message.callback_data:
                callback_data_handler(message)
            elif message.message_text:
                receive_text_message_handler(message)

    def start_waiting_handler(message: IncomingMessage):
        """Обработчик команды Старт от оператора.
        Включает оператора в словарь активных."""
        pass
        # self.set_operator_chat(message.user_id, message.chat_id)
        # print('start_waiting_handler')
        # if self.check_user_is_operator(message.user_id):
        #     # Проверяем, что оператор eще не назначен другому клиенту
        #     if self.check_operator_is_not_busy(message.user_id):
        #         # Отправляем оператору сообщения о переходе
        #         # в режим ожидания сообщений от клиентов.
        #         self.send_message(
        #             chat_id=message.chat_id,
        #             reply_markup=self.get_finish_keyboard(),
        #             message='Вы перешли в режим ожидания клиентов.'
        #         )
        #         # Включаем оператора в список активных.
        #         self.set_operator_active(message.user_id)
        #         # Рассылка уведомлений свободным операторам
        #         self.send_notification_for_available_operators()
        #     else:
        #         # Если оператор занят другим клиентом.
        #         self.alert_operator_is_busy(message)

    def finish_working_handler(message: IncomingMessage):
        """Обработчик..."""
        pass

    def callback_data_handler(message: IncomingMessage):
        """Обработчик..."""
        pass

    def receive_text_message_handler(message: IncomingMessage):
        """Обработчик..."""
        token, created = Token.objects.get_or_create(chat_token='any one')

        message_object = Message.objects.create(
            message=message.message_text, 
            token=token,
            status='0', 
            user="USER",
            telegram_number_chat=message.chat_id,
        )
        message_object.save()

    incoming_message_list = get_updates()
    
    parse_incoming_message(incoming_message_list)