from datetime import datetime, date
from logging import Logger
from typing import Optional
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup, ReplyMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters

from .models import LastUpdate, Operator, OperatorChat, Invite
from .tg_utils import IncomingMessage
from gpt.models import Message, Token


def check_is_in_operator_mode(chat_token: str) -> bool:
    """Проверяет, что пользователь переключен на оператора.
    Возвращает True при наличии активного OperatorChat c пользователем
    или действующих приглашений Invite для операторов."""
    token = Token.objects.filter(chat_token=chat_token)
    is_in_operator_chats = OperatorChat.objects.filter(token=token).exists()
    is_in_invites = Invite.objects.filter(token=token).exists()
    return is_in_operator_chats or is_in_invites


class VinkTgBotGetter():
    """Класс телеграмм бота для операторов."""

    def __init__(self, telegram_bot_token, logger: Logger):
        """Конструктор телеграмм бота.
        Аргументы:
            telegram_bot_token - токен бота
            logger: logging.Logger - объект логера.
        """
        self.logger = logger
        self.bot = Bot(token=telegram_bot_token)
    
    def run(self):
        """Запускает итерацию работы бота."""
        
        # Получаем обновления с телеграмма
        self.__get_and_parse_updates()

        # Рассылка уведомлений о новых сообщениях пользователей
        self.__send_invites_for_available_operators()

        # Рассылка сообщений операторам
        self.__send_client_messages()
    
    def __send_client_messages(self):
        """Рассылка сообщений операторам по действующим чатам."""
        
        messages = Message.objects.filter(
            is_handled=False, user='USER', recipient='OPERATOR')
        
        for item in messages:
            chat_id = self.__get_operator_id_by_client_token(
                item.token.chat_token)
            if chat_id:
                self.__send_message(
                    message=item.message,
                    chat_id=chat_id
                )
                item.is_handled = True
                item.save()

    def __get_finish_keyboard(self):
        """Возвращает клавиатуру с кнопкой Финиш."""
        button = KeyboardButton(text='/finish')
        return ReplyKeyboardMarkup([[button]])

    def __get_start_keyboard(self):
        """Возвращает клавиатуру с кнопкой Старт."""
        button = KeyboardButton(text='/start')
        return ReplyKeyboardMarkup([[button]])
    
    def __get_start_conversation_keyboard(self, client_token: str):
        """Возвращает клавиатуру с кнопкой Начать переписку с клиентом.
        В client_token передается в callback_data."""
        button = InlineKeyboardButton(
            text='Начать переписку с клиентом',
            callback_data=client_token)
        reply_markup = InlineKeyboardMarkup([[button]])
        return reply_markup    
    
    def __send_message(
        self, message: str, chat_id: int, 
        reply_markup: ReplyMarkup = None,
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
            self.logger.debug(
                f'Чат-бот удачно отправил сообщение: {message}.'
            )
        except Exception as exception:
            error_message = (
                f'Чат-бот не смог отправить сообщение: {message}. {exception}'
            )
            self.logger.error(error_message)
    
    def __get_and_parse_updates(self):
        """Получает и парсит обновления из телеграм."""
        incoming_messages = self.__get_updates()
        self.__parse_incoming_message(incoming_messages)

    def __get_updates(self) -> list[IncomingMessage]:
        """Получить обновления из телеграмм."""
        if LastUpdate.objects.exists():
            offset = LastUpdate.objects.first().update_id + 1
        else:
            offset = None

        updates: list[Update] = self.bot.get_updates(offset=offset)
        self.logger.debug('Bot get updates: ', len(updates), '.')
        result = []
        last_update_id = 0
        callback_data = None
        callback_query_id = None
        for update in updates:
            print(update)  # Дебаг принт
            # Если есть callback данные, извлекаем их. 
            # (это для кнопки начать переписку) 
            if hasattr(update, 'callback_query'):
                callback_query_id = getattr(update.callback_query, 'id', None)
                callback_data = getattr(update.callback_query, 'data', None)
            else:
                callback_data = None
                callback_query_id = None
            
            incoming_message = IncomingMessage(
                update_id=update.update_id,
                user_id=update.effective_user.id,
                user_first_name=getattr(update.effective_user, 'first_name'),
                user_last_name=getattr(update.effective_user, 'last_name'),
                user_username=getattr(update.effective_user, 'username'),
                message_text=update.effective_message.text,
                callback_data=callback_data,
                callback_query_id=callback_query_id,
                client_token=self.__get_client_token_by_operator(
                    update.effective_user.id)
            )
            last_update_id = update.update_id
            
            result.append(incoming_message)
        if offset:
            last_update_object = LastUpdate.objects.first()
            last_update_object.update_id = last_update_id
            last_update_object.save()
        else:
            LastUpdate.objects.create(update_id=last_update_id)
        
        return result
    
    def __parse_incoming_message(
            self, incoming_message_list: list[IncomingMessage]):
        """ Разбор списка сообщений."""
        for message in incoming_message_list:
            self.logger.debug(message)
            if message.message_text == '/start':
                self.__start_waiting_handler(message)
            elif message.message_text == '/finish':
                self.__finish_working_handler(message)
            elif message.callback_data:
                self.__callback_data_handler(message)
            elif message.message_text:
                self.__receive_text_message_handler(message)

    def __start_waiting_handler(self, message: IncomingMessage):
        """Обработчик команды Старт от оператора.
        Включает оператора в ActiveOperator."""
        user_id = message.user_id
        if self.__check_user_is_operator(user_id):
            if not self.__check_operator_is_active(user_id):
                
                # Отправляем оператору сообщения о переходе
                # в режим ожидания сообщений от клиентов.
                self.__send_message(
                    chat_id=message.user_id,
                    reply_markup=self.__get_finish_keyboard(),
                    message='Вы перешли в режим ожидания клиентов.'
                )
                # Включаем оператора в список активных.
                self.__set_operator_active(user_id)
            
            else:
                self.__message_operator_is_active_all_ready(message)
        else:
            # Команда не от оператора, создаем оператора не активным.
            self.__create_operator(message)
    
    def __create_operator(self, message: IncomingMessage):
        """Создает оператора с is_enabled = False."""
        Operator.objects.create(
            tg_user_id=message.user_id,
            first_name=message.user_first_name,
            last_name=message.user_last_name,
            username=message.user_username,
            is_enabled=False,
        )

    def __finish_working_handler(self, message: IncomingMessage):
        """Обработчик команды Финиш.
        Отправляем сообщение об окончании работы оператора.
        Закрывает чат оператора с клиентом.
        Исключает оператора из числа активных.
        """
        
        if self.__check_user_is_operator(message.user_id):
            self.__send_message(
                chat_id=message.user_id,
                reply_markup=self.__get_start_keyboard(),
                message=(
                    'Вы закончили работу. '
                    'Для перехода в режим ожидания '
                    'сообщений нажмите кнопку start.')
            )
            self.__detach_operator_and_client(message.user_id)
        else:
            self.logger.debug(
                f'Команда Финиш от пользователя {message.user_id},'
                'который не является оператором.' 
            )

    def __disable_invites(self, token: Token):
        """Выключает приглашения операторов для token."""
        invites_queryset = Invite.objects.filter(
            token=token, is_active=True)
        for invite in invites_queryset:
            invite.is_active = False
            invite.save()

    def __callback_data_handler(self, message: IncomingMessage):
        """Обработчик для кнопки Начать переписку с клиентом."""
        # self.logger.error('Вход в калбек')
        if self.__check_user_is_operator(message.user_id):
            # self.logger.error('Оператор - оператор')
            if self.__check_operator_is_waiting(message.user_id):
                # self.logger.error('Оператор в ожидании')
                # Уведомляем оператора о начале работы с клиентом
                self.__alert_operator_start_messaging_with_client(message)
                # Проверяем наличие токена из мессаджа в модели
                token = Token.objects.filter(
                    chat_token=message.callback_data).first()
                operator: Operator = Operator.objects.filter(
                    tg_user_id=message.user_id, is_enabled=True).first()
                operator_chat: OperatorChat = OperatorChat.objects.filter(
                    operator=operator, is_active=True,
                ).first() # token=None #  token__isnull=True, 
                # self.logger.error('Перед входом в оператор чат')
                # self.logger.error(message.callback_data)
                # self.logger.error(token)
                # self.logger.error(operator)
                # self.logger.error(operator_chat)
                # self.logger.error(operator_chat.token.chat_token)

                if token and operator and operator_chat.token is None:
                    # Изменяем запись в OperatorChat
                    # self.logger.error('Вошли в оператор чат здесь ставится токен')
                    operator_chat.token = token
                    operator_chat.save()
                    self.__disable_invites(token)
                    
                    # Отправляем оператору предшествующую переписку
                    # клиента с gpt и другими операторами за текущие сутки.
                    previous_chat = Message.objects.filter(
                        token=token,
                        date_create__gte=datetime.combine(
                            date.today(), datetime.min.time()
                        ),
                    ).exclude(is_handled=False).order_by('date_create')
                    
                    if len(previous_chat) > 0:
                        self.__send_message(
                            message=(
                                f'Предыдущая переписка с {token.chat_token}, '
                                f'всего {len(previous_chat)} сообщений:'
                            ),
                            chat_id=message.user_id
                        )
                        for item in previous_chat:
                            text = (
                                f'От: {item.user}\n'
                                f'Получатель: {item.recipient}\n'
                                f'{item.date_create}:\n'
                                f'{item.message}'
                            )
                            self.__send_message(
                                message=text,
                                chat_id=message.user_id
                            )
                    # Отправляем оператору все не обработанные сообщения
                    # от данного клиента
                    client_messages = Message.objects.filter(
                        token=token,
                        user='USER',
                        is_handled=False
                    )
                    if len(client_messages) > 0:
                        self.__send_message(
                            message=(
                                f'Необработанные сообщения от '
                                f'{token.chat_token}, '
                                f'всего {len(client_messages)} сообщений:'
                            ),
                            chat_id=message.user_id
                        )
                        for item in client_messages:
                            text = f'{item.date_create}:\n{item.message}'
                            self.__send_message(
                                message=text,
                                chat_id=message.user_id
                            )
                            item.is_handled = True
                            item.save()
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
                        f'токена {message.client_token} или оператор занят'
                    )
            else:
                # Оператор уже занят
                self.logger.debug(
                    'Callback от оператора, который не в режиме ожидания.'
                    f'{message.user_id} {message.user_username}'
                )
        else:
            # Команда не от оператора
            self.logger.debug(
                'Callback не от оператора, '
                f'{message.user_id} {message.user_username}'
            )

    def __receive_text_message_handler(self, message: IncomingMessage):
        """Обработчик текстового сообщения."""
        
        if (
            self.__check_token(message.client_token)
            and self.__check_user_is_operator(message.user_id)
            and self.__check_operator_chat_with_client(
                operator_user_id=message.user_id,
                client_token=message.client_token
            )
        ):
            token = Token.objects.filter(
                chat_token=message.client_token).first()
            message_object = Message.objects.create(
                message=message.message_text,
                token=token,
                status='0',
                user='OPERATOR',
                telegram_number_chat=message.user_id,
            )
            message_object.save()
    
    def __check_token(self, token: str) -> bool:
        """Возвращает True если токен зарегистрирован."""
        return Token.objects.filter(chat_token=token).exists()

    def __send_invites_for_available_operators(self):
        """Рассылает уведомления свободным операторам.
        Об ожидающих клиентах."""
        
        # Получить список свободных операторов
        operator_waiting_set = set(
            OperatorChat.objects.filter(
                is_active=True, token__isnull=True
            ).values_list(
                'operator__tg_user_id', flat=True
            )
        )

        # Операторам приглашения о новых не обработанных
        # запросах пользователей.
        tokens = set(
            Message.objects.filter(
                is_handled=False, user='USER', recipient='OPERATOR'
            ).values_list('token__chat_token', flat=True)
        )
        
        for chat_id in operator_waiting_set:
            for chat_token in tokens:
                invite, created = Invite.objects.get_or_create(
                    token=self.__get_token(chat_token),
                    operator=self.__get_operator(chat_id),
                )
                if created:
                    self.__send_message(
                        chat_id=chat_id,
                        reply_markup=self.__get_start_conversation_keyboard(
                            chat_token),
                        message=f'Новое сообщение от клиента {chat_token}.'
                    )
                

    def __get_token(self, token: str) -> Optional[Token]:
        """Возвращает объект Token по строковому токену.
        если не найден None."""
        token_object: Token = Token.objects.filter(chat_token=token).first()
        return token_object
    
    def __get_operator(self, user_id: int) -> Optional[Operator]:
        """Возвращает объект Operator по tg_user_id (int).
        если не найден None."""
        operator_object: Operator = Operator.objects.filter(
            tg_user_id=user_id
        ).first()
        return operator_object

    def __check_user_is_operator(self, user_id: int) -> bool:
        """Проверяет является ли пользователь ТГ,
        отправивший сообщение боту, - оператором."""
        operator: Operator = Operator.objects.filter(
            tg_user_id=user_id, is_enabled=True).first()
        if operator:
            return True
        return False
    
    def __get_client_token_by_operator(self, user_id: int) -> Optional[str]:
        """Возвращает токен клиента, назначенного оператору для разговора."""
        operator: Operator = Operator.objects.filter(
            tg_user_id=user_id, is_enabled=True).first()
        operator_chat: OperatorChat = OperatorChat.objects.filter(
            operator=operator, is_active=True).first()
        if operator_chat:
            if operator_chat.token:
                return operator_chat.token.chat_token
        return None
    
    def __get_operator_id_by_client_token(self, client_token: str) -> int:
        """Возвращает user_id телеграмм оператора по токену клиента.
        Если не найден - None."""
        operator_chat: OperatorChat = OperatorChat.objects.filter(
            token__chat_token=client_token, is_active=True).first()
        if operator_chat:
            return operator_chat.operator.tg_user_id
    
    def __detach_operator_and_client(self, operator_user_id):
        """Удаляет связи между оператором и клиентом в конце разговора.
        Закрывает чат оператора с клиентом.
        Удаляет запись из ActiveOperator."""
        client_token = self.__get_client_token_by_operator(operator_user_id)
        if client_token:
            operator_chat: OperatorChat = OperatorChat.objects.filter(
                token__chat_token=client_token,
                operator__tg_user_id=operator_user_id,
                is_active=True
            ).first()
            if operator_chat:
                operator_chat.is_active = False
                operator_chat.save()
            else:
                self.logger.error(
                    f'Отключение не активного оператора {operator_user_id}.'
                )
        else:
            self.logger.error(
                f'Отключение оператора {operator_user_id}, которому '
                'не назначен клиент.'
            )
    
    def __check_operator_chat_with_client( 
            self, operator_user_id: int, client_token: str = None
    ) -> bool:
        """Проверяет что оператор в чате с клиентом.
        Если не в чате возвращает - False,
        Если назначен клиенту client_token, возвращает - True."""
        operator: Operator = self.__get_operator(user_id=operator_user_id)
        operator_chat: OperatorChat = OperatorChat.objects.filter(
            operator=operator, is_active=True, token__chat_token=client_token
            ).first()
        return operator_chat is not None
    
    def __check_operator_is_waiting(
            self, operator_user_id: int
    ) -> bool:
        """Проверяет что оператор активен и не назначен другому клиенту.
        Если не занят (активен и не назначен какому-либо другому клиенту)
        возвращает - False,
        Если не активен или назначен другому клиенту, возвращает - True."""
        operator: Operator = self.__get_operator(user_id=operator_user_id)
        operator_chat: OperatorChat = OperatorChat.objects.filter(
            operator=operator, is_active=True, token__isnull=True
            ).first()
        return operator_chat is not None
    
    def __check_operator_is_active(
            self, operator_user_id: int,
    ) -> bool:
        """Проверяет что оператор активен, т.е. 
        ожидает приглашений или уже работает с клиентом."""
        operator: Operator = self.__get_operator(user_id=operator_user_id)
        operator_chat: OperatorChat = OperatorChat.objects.filter(
            operator=operator, is_active=True).first()
        return operator_chat is not None
    
    def __set_operator_active(self, operator_user_id: int):
        """Вносит оператора в список активных операторов."""
        operator: Operator = self.__get_operator(user_id=operator_user_id)
        operator_chat, created = OperatorChat.objects.get_or_create(
            operator=operator, is_active=True, token=None
        )
    
    def __message_operator_is_active_all_ready(self, message: IncomingMessage):
        """Отправляет оператору предупреждение о том,
        что он уже находится в режиме ожидания."""
        text = (
            'Вы уже в режиме в ожидания.'
        )
        self.__send_message(
            message=text,
            chat_id=message.user_id,
        )
    
    def __alert_operator_start_messaging_with_client(
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
    