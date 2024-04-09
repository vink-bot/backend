# Хакатон от Яндекс и Vink.RU
### Проект чата с Yandex GPT - это инновационное решение для взаимодействия с посетителями вашего сайта. Он использует мощь искусственного интеллекта от Yandex GPT для обеспечения автоматизированных ответов на запросы пользователей.

### Основные функции
- Использование Yandex GPT: Интеграция с Yandex GPT позволяет чату генерировать интеллектуальные ответы на запросы пользователей, что улучшает опыт обслуживания и снижает нагрузку на операторов.

- Автоматическое переключение на оператора: Если пользователь запросит помощь или чат не сможет обработать запрос, система автоматически переключится на живого оператора для обеспечения высококачественного обслуживания.

- Интеграция с веб-сайтом: Проект чата легко интегрируется с вашим веб-сайтом, обеспечивая плавный и интуитивно понятный интерфейс для пользователей.

- Пользовательский интерфейс: Чат обладает удобным пользовательским интерфейсом с возможностью отправки сообщений, получения автоматических ответов и запроса помощи оператора.

- Адаптивность: Чат адаптирован для работы на различных устройствах, включая десктопы, планшеты и мобильные телефоны.

#  Локальная работа с репозиторием (без frontend'a)

- Клонируйте репозиторий
```
git clone git@github.com:vink-bot/backend.git
```

- Запросите .env файл у разработчиков (разместите в одной директории с Readme)

- Запустите docker локально. Перейдите в директорию с файлом docker-compose.yml и выполните команду
```
docker-compose up --build
```

- Перейдите в контейнер backend (например через локальный докер в визуальном режиме), создайте суперюзера.
```
python manage.py createsuperuser
```

- API (version 1) будет доступен по url:
http://127.0.0.1:8000/api/v1/
- Админка будет доступна по url:
http://127.0.0.1:8000/admin/
- Flower(отслеживание задач celery) будет доступty по url:
http://127.0.0.1:5555

- Логика
Фронт отправляет POST запрос на http://127.0.0.1:8000/gpt/ передает в теле запроса сообщение от пользователя, например
```
{
    "message": "Торгуете?"
}
```
и в Headers передает токен пользователя (токен генерит фронт), например
```
{
    "chat-token": "serw45ge45v45ygv45yb5454"
}
```
- Создается запись в таблице Message с сообщением пользователя и таблице Token(если его ранее не было)
- Фронт получает сразу ответ 201 либо 400. И задача улетает в celery-worker. Там данное сообщение отправляем в yandexGPT и получаем ответ(от yandexGPT). Создается запись в таблице Message с сообщением от GPT.
- Фронт шлет периодически GET запрос на http://127.0.0.1:8000/message/ (в Headers передает токен пользователя).
- По токену достаем все сообщения со status = "0" (меняем на status = "1") и отдаем их фронту в виде
```
{
    "messages": [
        {
            "message": "Могу предложить вам список товаров синего цвета, которые есть на нашем сайте.",
            "date_create": "2024-04-09T06:31:23.609730Z",
            "user": "GPT"
        },
        {
            "message": "Да, мы торгуем такими товарами.",
            "date_create": "2024-04-09T06:32:02.609730Z",
            "user": "GPT"
        }
    ]
}
```
- Так продолжается до тех пор, пока gpt явно не ответит, как бот, в таком случае, сообщение от gpt пользователю не доставляется, а подключается оператор(человек) через тг бота, который получает всю переписку пользователя с gpt. И далее продолжает общение с пользователем.

# Инструкция по работе оператора через телеграмм-бот.
- https://disk.yandex.ru/i/1Km42IVc3MpENg
- Внимательно прочитайте инструкцию. Обращаем внимание, что при первом посещении бота - нужно нажать «Start». Далее в админке администратору необходимо подтвердить (активировать) оператора - http://hackathon.zapto.org/admin/tg/operator/
- После этого (что бы принимать сообщения от пользователей) - необходимо вновь нажать «Start».

# Ссылка на бота ТГ (для операторов) - что бы через него общаться с пользователем/ями.
- https://t.me/TigerKitty_bot

# Сайт проекта
- http://hackathon.zapto.org/
#### Админка
- логин "admin" пароль "123"
- http://hackathon.zapto.org/admin/

# Демо работы проекта.
- https://disk.yandex.ru/i/oFe1ww9htkyEiA

# Авторы (backend):
➡️ Александр Мальшаков (ТГ [@amalshakov](https://t.me/amalshakov), GitHub [amalshakov](https://github.com/amalshakov/))
➡️ Олег Чужмаров  (ТГ [@amalshakov](https://t.me/chtiger4), GitHub [floks41](https://github.com/floks41/))

# Авторы
➡️ Frontend - Типсин Дмитрий (ТГ [@Chia_Rio_Ru](https://t.me/Chia_Rio_Ru), GitHub [TIPDMR](https://github.com/TIPDMR/))
➡️ Product manager – Сергей Кириллов (ТГ [@Exclussivei](https://t.me/Exclussivei))
➡️ Project manager – Лена Вертинская (ТГ [@lena_vert](https://t.me/lena_vert))

# Ссылка на репозиторий frontend'a (переключите на ветку develop):
- https://github.com/vink-bot/frontend
