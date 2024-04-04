from datetime import datetime, date
from django.db.models import Q
from logging import Logger
from typing import Optional
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup, ReplyMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters

from .models import Message, LastUpdate, Token, Operator, ActiveOperator, OperatorChat
from .tg_utils import IncomingMessage


class VinkTgBotGetter():
    """Класс телеграмм бота для операторов."""

    def __init__(self, telegram_bot_token, logger: Logger):
        """Конструктор телеграмм бота.
        Аргументы:
            telegram_bot_token - токен бота
            logger: logging.Logger - объект логера.
        """
        self.logger = logger

        # Объекты телеграм бота
        self.bot = Bot(token=telegram_bot_token)
    
    def run(self):
        """Запускает итерацию работы бота."""
        
        # Получаем обновления с телеграмма
        self.get_and_parse_updates()

        # Рассылка уведомлений о новых сообщениях пользователей
        self.send_notification_for_available_operators()

        # Рассылка сообщений операторам
        self.send_client_messages()
    
    def send_client_messages():
        """Рассылка сообщений операторам по действующим чатам."""
        
        messages = Message.objects.filter(status='0', user='USER')

    
    def get_finish_keyboard(self):
        """Возвращает клавиатуру с кнопкой Финиш."""
        button = KeyboardButton(text='/finish')
        return ReplyKeyboardMarkup([[button]])

    def get_start_keyboard(self):
        """Возвращает клавиатуру с кнопкой Старт."""
        button = KeyboardButton(text='/start')
        return ReplyKeyboardMarkup([[button]])
    
    def get_start_conversation_keyboard(self, client_token: str):
        """Возвращает клавиатуру с кнопкой Начать переписку с клиентом.
        В client_token передается в callback_data."""
        button = InlineKeyboardButton(
            text='Начать переписку с клиентом',
            callback_data=client_token)
        reply_markup = InlineKeyboardMarkup([[button]])
        return reply_markup    
    
    def send_message(
            self, message: 
            str, chat_id: int, 
            reply_markup: ReplyMarkup = None
        ):
        """
        Отправляет сообщения в телеграм-бот.
        Параметры:
            message (str): сообщение для отправки
            chat_id: идентификатор чата,
            reply_markup: клавиатура для отправки с сообщением,
        В случае ошибки логгирует исключение.
        """
        try:
            self.bot.send_message(
                chat_id=chat_id,
                reply_markup=reply_markup,
                text=message
            )
            self.logger.debug(f'Чат-бот удачно отправил сообщение: {message}.')
        except Exception as exception:
            error_message = f'Чат-бот не смог отправить сообщение: {message}. {exception}'
            self.logger.error(error_message)
    
    def get_and_parse_updates(self):
        """Получает и парсит обновления из телеграм."""
        incoming_messages = self.get_updates()
        self.parse_incoming_message(incoming_messages)

    def get_updates(self) -> list[IncomingMessage]:
        """Получить обновления из телеграмм."""
        if LastUpdate.objects.exists():
            offset = LastUpdate.objects.first().update_id + 1
        else:
            offset = None

        updates: list[Update] = self.bot.get_updates(offset=offset)
        self.logger.debug('Bot get updates: ', len(updates), '.')
        result = []
        last_update_id = 0
        for update in updates:

            # callback_data: str = None
            # callback_query_id: str = None
            # if update.callback_query:
            #     callback_data = update.callback_query.data
            #     callback_query_id = update.callback_query.id
            incoming_message = IncomingMessage(
                update_id=update.update_id,
                chat_id=update.effective_chat.id,
                user_id=update.effective_user.id,
                user_first_name=getattr(update.effective_user, 'first_name'),
                user_last_name=getattr(update.effective_user, 'last_name'),
                user_username=getattr(update.effective_user, 'username'),
                message_text=update.effective_message.text,
                callback_data=getattr(getattr(update, 'callback_query'), 'data'),
                callback_query_id=getattr(getattr(update, 'callback_query'), 'id'),
            )
            last_update_id = update.update_id
            
            result.append(incoming_message)
        if offset:
            LastUpdate.objects.first().update_id = last_update_id
        else:
            LastUpdate.objects.create(update_id=last_update_id)
        
        return result
    
    def parse_incoming_message(
            self, incoming_message_list: list[IncomingMessage]):
        """ Разбор списка сообщений."""
        for message in incoming_message_list:
            self.logger.debug(message)
            if message.message_text == '/start':
                self.start_waiting_handler(message)
            elif message.message_text == '/finish':
                self.finish_working_handler(message)
            elif message.callback_data:
                self.callback_data_handler(message)
            elif message.message_text:
                self.receive_text_message_handler(message)

    def start_waiting_handler(self, message: IncomingMessage):
        """Обработчик команды Старт от оператора.
        Включает оператора в ActiveOperator."""
        user_id = message.user_id
        if self.check_user_is_operator(user_id):
            if not self.check_operator_is_active(user_id):
                if self.check_operator_is_not_busy(user_id):
                    # Отправляем оператору сообщения о переходе
                    # в режим ожидания сообщений от клиентов.
                    self.send_message(
                        chat_id=message.chat_id,
                        reply_markup=self.get_finish_keyboard(),
                        message='Вы перешли в режим ожидания клиентов.'
                    )
                    # Включаем оператора в список активных.
                    self.set_operator_active(user_id, message.chat_id)
                else:
                    self.message_operator_is_busy(message)
            else:
                self.message_operator_is_active_all_ready(message)
        else:
            # Команда не от оператора, создаем оператора не активным.
            self.create_operator(message)
    
    def create_operator(self, message: IncomingMessage):
        """Создает оператора с is_enabled = False."""
        Operator.objects.create(
            tg_user_id=message.user_id,
            first_name=message.user_first_name,
            last_name=message.user_last_name,
            username=message.user_username,
            is_enabled=False,
        )

    def finish_working_handler(self, message: IncomingMessage):
        """Обработчик команды Финиш.
        Отправляем сообщение об окончании работы оператора.
        Закрывает чат оператора с клиентом.
        Исключает оператора из числа активных.
        """
        
        if self.check_user_is_operator(message.user_id):
            self.send_message(
                chat_id=message.chat_id,
                reply_markup=self.get_start_keyboard(),
                message=(
                    'Вы закончили работу. '
                    'Для перехода в режим ожидания '
                    'сообщений нажмите кнопку start.')
            )
            self.detach_operator_and_client(message.user_id)
        else:
            self.logger.debug(
                f'Команда Финиш от пользователя {message.user_id},'
                'который не является оператором.' 
            )

    def callback_data_handler(self, message: IncomingMessage):
        """Обработчик для кнопки Начать переписку с клиентом."""
        
        if self.check_user_is_operator(message.user_id):
            if self.check_operator_is_not_busy(message.user_id):
                # Уведомляем оператора о начале работы с клиентом
                self.alert_operator_start_messaging_with_client(message)
                # Проверяем наличие токена из мессаджа в модели
                token = Token.objects.first(token=message.client_token)
                if token:
                    # Создаем запись в OperatorChat
                    OperatorChat.objects.create(
                        token=message.client_token,
                        operator_user_id=message.user_id,
                        operator_chat_id=message.chat_id,
                        is_active=True
                    )
                    # Отправляем оператору предшествующую переписку
                    # клиента с gpt и другими операторами за текущие сутки.
                    previous_chat = Message.objects.filter(
                        token=token,
                        date_create__gte=datetime.combine(
                            date.today(), datetime.min.time()
                        ),
                    ).exclude(status='0').order_by('date_create')
                    
                    if len(previous_chat) > 0:
                        self.send_message(
                            message=(
                                f'Предыдущая переписка с клиентом {token}, '
                                f'всего {len(previous_chat)}:'
                            ),
                            chat_id=message.chat_id
                        )
                        for item in previous_chat:
                            text = (
                                f'{item.user}\n'
                                f'{item.date_create}:\n'
                                f'{item.message}'
                            )
                            self.send_message(
                                message=text,
                                chat_id=message.chat_id
                            )
                    # Отправляем оператору все неотправленные сообщения
                    # от данного клиента
                    client_messages = Message.objects.filter(
                        token=token,
                        user='USER',
                        status='0'
                    )
                    if len(client_messages) > 0:
                        self.send_message(
                            message=(
                                f'Сообщения от клиента {token},'
                                f'всего {len(client_messages)}:'
                            ),
                            chat_id=message.chat_id
                        )
                        for item in client_messages:
                            text = f'{item.date_create}:\n{item.message}'
                            self.send_message(
                                message=text,
                                chat_id=message.chat_id
                            )
                    else:
                        # Колбак и нет сообщений от клиента
                        self.logger.debug(
                            'Callback и нет сообщений от клиента '
                            f'токена {message.client_token}'
                        )
                else:
                    # Колбак сообщение с незарегистрированным токеном
                    self.logger.debug(
                        'Callback от незарегистрированного'
                        f'токена {message.client_token}'
                    )
            else:
                # Оператор уже занят
                self.logger.debug(
                    'Callback от оператора, который уже занят '
                    f'{message.user_id} {message.user_username}'
                )
        else:
            # Команда не от оператора
            self.logger.debug(
                'Callback не от оператора, '
                f'{message.user_id} {message.user_username}'
            )

    def receive_text_message_handler(self, message: IncomingMessage):
        """Обработчик текстового сообщения."""
        
        if (
            self.check_token(message.client_token)
            and self.check_user_is_operator(message.user_id)
            and self.check_operator_is_not_busy(
                operator_user_id=message.user_id,
                client_token=message.client_token
            )
        ):
            token = Token.objects.first(chat_token=message.client_token)
            message_object = Message.objects.create(
                message=message.message_text,
                token=token,
                status='0',
                user='OPERATOR',
                telegram_number_chat=message.chat_id,
            )
            message_object.save()
    
    def check_token(self, token: str) -> bool:
        """Возвращает True если токен зарегистрирован."""
        return Token.objects.filter(token=token).exists()

    def send_notification_for_available_operators(self):
        """Рассылает уведомления свободным операторам.
        Об ожидающих клиентах."""
        
        # Получить список свободных операторов
        
        user_chats_set = set(
            OperatorChat.objects.filter(
                is_active=True
            ).values_list(
                'operator_chat_id', flat=True
            )
        )
        
        active_user_chat_set = set(
            ActiveOperator.objects.all().values_list(
                'operator_chat_id', flat=True))
        
        user_waiting_set = active_user_chat_set - user_chats_set

        # Операторам приглашения о новых запросах пользователей.
        tokens = set(
            Message.objects.filter(
                status='0', user='USER'
            ).values_list('token', flat=True)
        )
        for chat_id in user_waiting_set:
            for token in tokens:
                self.send_message(
                    chat_id=chat_id,
                    reply_markup=self.get_start_conversation_keyboard(
                        token),
                    message=f'Новое сообщение от клиента {token}.'
                )
    
    def check_user_is_operator(self, user_id: int) -> bool:
        """Проверяет является ли пользователь ТГ,
        отправивший сообщение боту, - оператором."""
        operator: Operator = Operator.objects.first(
            tg_user_id=user_id, is_enabled=True)
        if operator:
            return True
        return False
    
    def get_client_token_by_operator(self, user_id: int) -> Optional[str]:
        """Возвращает токен клиента, назначенного оператору для разговора."""
        operator_chat: OperatorChat = OperatorChat.objects.first(
            operator_user_id=user_id, is_active=True)
        if operator_chat:
            return operator_chat.token
        return None
    
    def get_operator_id_by_client_token(self, client_token: str) -> int:
        """Возвращает user_id телеграмм оператора по токену клиента.
        Если не найден - None."""
        operator_chat: OperatorChat = OperatorChat.objects.first(
            token=client_token, is_active=True)
        if operator_chat:
            return operator_chat.operator_user_id
        return None
    
    def assign_operator_to_client(self, operator_user_id: int, client_token: str):
        """Назначает оператора клиенту."""
        active_operator: ActiveOperator = ActiveOperator.objects.first(operator_user_id=operator_user_id)
        assigned_token = self.get_client_token_by_operator(operator_user_id)
        if active_operator and assigned_token is None:
            OperatorChat.objects.create(
                token=client_token,
                operator_user_id=operator_user_id,
                operator_chat_id=active_operator.operator_chat_id,
            )
        else:
            self.logger.error(
                f'Клиенту {client_token} назначается '
                f'не активный оператор {operator_user_id}.'
            )
    
    def detach_operator_and_client(self, operator_user_id):
        """Удаляет связи между оператором и клиентом в конце разговора.
        Закрывает чат оператора с клиентом.
        Удаляет запись из ActiveOperator."""
        client_token = self.get_client_token_by_operator(operator_user_id)
        if client_token:
            operator_chat: OperatorChat = OperatorChat.objects.first(
                token=client_token, 
                operator_user_id=operator_user_id, 
                is_active=True
            )
            if operator_chat:
                operator_chat.is_active = False
                operator_chat.save()
            
            active_operator: ActiveOperator = ActiveOperator.objects.first(
                operator_user_id=operator_user_id)
            if active_operator:
                active_operator.delete()
            else:
                self.logger.error(
                    f'Отключение не активного оператора {operator_user_id}.'
                )
        else:
            self.logger.error(
                f'Отключение оператора {operator_user_id}, которому '
                'не назначен клиент.'
            )
    
    def check_operator_is_not_busy(
            self, operator_user_id: int, client_token: str = None
    ) -> bool:
        """Проверяет что оператор не занят, другим клиентом.
        Если занят (назначен какому-либо другому клиенту) возвращает - False,
        Если назначен клиенту client_token, возвращает - True."""
        current_client_token = self.get_client_token_by_operator(
            operator_user_id)
        return current_client_token == client_token
    
    def check_operator_is_active(
            self, operator_user_id: int,
    ) -> bool:
        """Проверяет что оператор активен, т.е. 
        ожидает приглашений или уже работает с клиентом."""
        active_operator: ActiveOperator = ActiveOperator.objects.first(
            operator_user_id=operator_user_id)
        return active_operator is not None
    
    def set_operator_active(self, operator_user_id: int, operator_chat_id: int):
        """Вносит оператора в список активных операторов."""
        ActiveOperator.objects.get_or_create(
            operator_user_id=operator_user_id,
            operator_chat_id=operator_chat_id,
        )

    def message_operator_is_busy(self, message: IncomingMessage):
        """Отправляет оператору предупреждение о том,
        что он уже назначен другому клиенту."""
        text = (
            'Вы уже вступили в переписку с клиентом'
            f'{self.get_client_token_by_operator(message.user_id)}. '
            'Все Ваши сообщения пересылаются клиенту!'
        )
        self.send_message(
            message=text,
            chat_id=message.chat_id,
        )
    
    def message_operator_is_active_all_ready(self, message: IncomingMessage):
        """Отправляет оператору предупреждение о том,
        что он уже находится в режиме ожидания."""
        text = (
            'Вы уже в режиме в ожидания.'
        )
        self.send_message(
            message=text,
            chat_id=message.chat_id,
        )
    
    def alert_operator_start_messaging_with_client(
            self, message: IncomingMessage):
        """Отправляет оператору предупреждение
        о начале переписки с клиентом."""
        text = (
            f'Вы вступили в переписку с клиентом {message.client_token}. '
            'Все последующие Ваши сообщения будут пересланы клиенту!'
        )
        self.bot.answer_callback_query(
            callback_query_id=message.callback_query_id,
            text=text,
            show_alert=True
        )
    
    