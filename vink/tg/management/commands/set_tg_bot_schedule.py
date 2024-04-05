from django.core.management import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule

from datetime import datetime, timedelta


class Command(BaseCommand):
    """Административная команда для установки расписания
    запуска телеграмм-бота."""

    help = (
        'Устанавливает расписание запуска телеграм-бота.'
        'Период запуска каждые 15 секунд.'
    )

    def handle(self, *args, **options):
        """Исполнение административной команды."""

        schedule, created = IntervalSchedule.objects.get_or_create(
            every=15,
            period=IntervalSchedule.SECONDS,
        )
        PeriodicTask.objects.create(
            interval=schedule,
            name='Telegram bot get and process updates',
            task='tasks.get_and_process_tg_updates',  
            # expires=datetime.utcnow() + timedelta(seconds=25)
        )