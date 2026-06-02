from django.core.management.base import BaseCommand
from weather.models import GardenPlot
from weather.services.recommendation_engine import generate_for_plot


class Command(BaseCommand):
    help = 'Генерирует рекомендации для всех участков на основе прогноза погоды.'

    def handle(self, *args, **options):
        total = 0
        for plot in GardenPlot.objects.all():
            count = generate_for_plot(plot)
            total += count
            self.stdout.write(f'{plot.name} ({plot.user.username}): +{count}')
        self.stdout.write(self.style.SUCCESS(f'Всего создано рекомендаций: {total}'))