from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Загрузка фикстур в базу данных.'

    def add_arguments(self, parser):
        parser.add_argument('fixture_name', type=str)

    def handle(self, *args, **options):
        fixture_name = options.get('fixture_name')
        self.stdout.write(f'Загружаем фикстуру "{fixture_name}"...')

        try:
            call_command('loaddata', fixture_name)
            self.stdout.write(self.style.SUCCESS(
                f'Фикстура "{fixture_name}" успешно загружена.'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(
                f'Ошибка при загрузке фикстуры: {e}'))
