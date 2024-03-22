#  Работа с репозиторием
- клонируйте репозиторий
```
git clone git@github.com:vink-bot/backend.git
```
- Перейдите в папку с проектом (vink_backend), создайте виртуальное окружение. Активируйте его.
```
python -m venv venv
source venv/Scripts/activate
```
- Установите зависимости (библиотеки)
```
pip install -r requirements.txt
```
- Перейдите в папку с файлом manage.py, создайте миграции, примените миграции. Запустите сервер локально.
```
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
- Swagger RESTful API Documentation Specification будет доступен по url:
http://127.0.0.1:8000/swagger/
- API (version 1) будет доступен по url:
http://127.0.0.1:8000/api/v1/

# vink_backend
Разработка чат-бота с технологией GPT на сайт компании для предоставления консультаций по материалам и оборудованию, а также оказания помощи клиентам 24/7.
