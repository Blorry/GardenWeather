from django.core.management.base import BaseCommand
from weather.models import Region, WeatherRecord
from weather.services.weather_api import fetch_forecast, aggregate_daily


class Command(BaseCommand):
    help = 'Загружает прогноз погоды из OpenWeatherMap для всех регионов.'

    def handle(self, *args, **options):
        total = 0
        for region in Region.objects.all():
            try:
                items = fetch_forecast(region)
            except Exception as exc:
                self.stderr.write(f'{region.name}: {exc}')
                continue

            days = aggregate_daily(items)
            for day in days:
                WeatherRecord.objects.update_or_create(
                    region=region, date=day['date'],
                    defaults={
                        'temp_min': day['temp_min'],
                        'temp_max': day['temp_max'],
                        'humidity': day['humidity'],
                        'precipitation': day['precipitation'],
                    },
                )
                total += 1
            self.stdout.write(f'{region.name}: загружено {len(days)} дней')
        self.stdout.write(self.style.SUCCESS(f'Всего записей обновлено: {total}'))