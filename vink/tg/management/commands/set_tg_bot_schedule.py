from django.core.management import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule

INTERVAL_SECONDS = 15


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
            every=INTERVAL_SECONDS,
            period=IntervalSchedule.SECONDS,
        )
        PeriodicTask.objects.create(
            interval=schedule,
            name='Telegram bot get and process updates.',
            task='tasks.get_and_process_tg_updates',
        )
