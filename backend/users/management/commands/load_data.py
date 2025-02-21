import csv
import logging

from django.core.management.base import BaseCommand

from users.models import Ingredient


class Command(BaseCommand):
    """
    Импорт данных из CSV-файла в базу данных (модель Ingredient).
    """
    help = 'Импорт данных из CSV-файла в модель Ingredient'

    def add_arguments(self, parser):
        """
        Определяет аргумент командной строки для указания пути к CSV-файлу.
        """
        parser.add_argument(
            '--path',
            type=str,
            help='Путь к CSV-файлу с данными ингредиентов.',
        )

    def handle(self, *args, **options):
        """
        Обрабатывает импорт данных из CSV-файла в модель Ingredient.
        """
        csv_file_path = options['path']
        if not csv_file_path:
            self.stdout.write(
                self.style.ERROR(
                    'Не указан путь к CSV-файлу.'
                    'Используйте --path <путь_к_файлу>.'
                )
            )
            return

        success_count = 0
        error_count = 0
        try:
            with open(
                    csv_file_path,
                    'r',
                    encoding='utf-8',
            ) as csvfile:
                reader = csv.reader(csvfile)
                for row_number, row in enumerate(reader, start=1):
                    if len(row) != 2:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Строка {row_number} пропущена: '
                                f'неверное количество столбцов ({len(row)}).'
                            )
                        )
                        error_count += 1
                        continue

                    name, measurement_unit = row
                    try:
                        ingredient, created = Ingredient.objects.get_or_create(
                            name=name, measurement_unit=measurement_unit
                        )
                        if created:
                            success_count += 1
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Ингредиент "{name}" успешно добавлен.'
                                )
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'Ингредиент "{name}" уже существует.'
                                )
                            )
                    except Exception as e:
                        error_count += 1
                        logging.exception(
                            f'Ошибка при обработке строки {row_number}: {e}'
                        )
                        self.stdout.write(
                            self.style.ERROR(
                                f'Ошибка добавления ингредиента {name}: {e}'
                            )
                        )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Импорт завершен. Добавлено: {success_count}, '
                    f'Ошибок: {error_count}.'
                )
            )

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'Файл "{csv_file_path}" не найден.')
            )
        except Exception as e:
            logging.exception(f'Общая ошибка импорта: {e}')
            self.stdout.write(self.style.ERROR(f'Общая ошибка импорта: {e}'))
