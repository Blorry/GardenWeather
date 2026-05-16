from django.core.management.base import BaseCommand
from weather.models import Region, Culture


REGIONS = [
    ('Москва', 55.7558, 37.6173, 'central'),
    ('Санкт-Петербург', 59.9343, 30.3351, 'north'),
    ('Краснодар', 45.0355, 38.9753, 'south'),
    ('Новосибирск', 55.0084, 82.9357, 'north'),
    ('Воронеж', 51.6720, 39.1843, 'central'),
]

CULTURES = [
    ('Томаты', 'Теплолюбивая культура, требует рассады.', 15, 30, 110),
    ('Огурцы', 'Любит тепло и влагу.', 18, 32, 60),
    ('Картофель', 'Универсальная культура.', 8, 25, 90),
    ('Морковь', 'Холодостойкая, прямой посев.', 5, 22, 100),
    ('Капуста белокочанная', 'Холодостойкая, влаголюбивая.', 7, 24, 130),
    ('Перец сладкий', 'Очень теплолюбивый.', 18, 32, 120),
    ('Свёкла', 'Неприхотливая, любит свет.', 8, 25, 100),
    ('Лук репчатый', 'Холодостойкий.', 4, 22, 90),
    ('Кабачки', 'Теплолюбивые, быстро растут.', 15, 30, 50),
    ('Редис', 'Скороспелая, прохладолюбивая.', 5, 20, 25),
    ('Чеснок', 'Озимый и яровой, холодостойкий.', 3, 22, 100),
    ('Клубника', 'Многолетняя, любит солнце.', 10, 25, 60),
]


class Command(BaseCommand):
    help = 'Заполняет БД начальными данными: регионы и культуры.'

    def handle(self, *args, **options):
        for name, lat, lon, zone in REGIONS:
            Region.objects.get_or_create(
                name=name,
                defaults={'latitude': lat, 'longitude': lon, 'climate_zone': zone},
            )
        for name, desc, t_min, t_max, days in CULTURES:
            Culture.objects.get_or_create(
                name=name,
                defaults={
                    'description': desc,
                    'min_planting_temp': t_min,
                    'max_planting_temp': t_max,
                    'vegetation_days': days,
                },
            )
        self.stdout.write(self.style.SUCCESS(
            f'Загружено: {Region.objects.count()} регионов, {Culture.objects.count()} культур'
        ))