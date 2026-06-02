from django.core.management.base import BaseCommand
from weather.models import Region, Culture


REGIONS = [
    ('Московская область', 55.7558, 37.6173, 'central', 'clay'),
    ('Ленинградская область', 59.9343, 30.3351, 'north', 'sandy'),
    ('Краснодарский край', 45.0355, 38.9753, 'south', 'chernozem'),
    ('Воронежская область', 51.6720, 39.1843, 'central', 'chernozem'),
    ('Новосибирская область', 55.0084, 82.9357, 'north', 'chernozem'),
    ('Свердловская область', 56.8389, 60.6057, 'north', 'podzolic'),
]

CULTURES = [
    ('Томаты', 'Теплолюбивая культура, требует рассады.', 15, 30, 110, 5, 6),
    ('Огурцы', 'Любит тепло и влагу.', 18, 32, 60, 5, 6),
    ('Картофель', 'Универсальная культура.', 8, 25, 90, 4, 5),
    ('Морковь', 'Холодостойкая, прямой посев.', 5, 22, 100, 4, 6),
    ('Капуста белокочанная', 'Холодостойкая, влаголюбивая.', 7, 24, 130, 4, 6),
    ('Перец сладкий', 'Очень теплолюбивый.', 18, 32, 120, 5, 6),
    ('Свёкла', 'Неприхотливая, любит свет.', 8, 25, 100, 4, 6),
    ('Лук репчатый', 'Холодостойкий.', 4, 22, 90, 4, 5),
    ('Кабачки', 'Теплолюбивые, быстро растут.', 15, 30, 50, 5, 6),
    ('Редис', 'Скороспелая, прохладолюбивая.', 5, 20, 25, 4, 9),
    ('Чеснок', 'Озимый, холодостойкий.', 3, 22, 100, 10, 11),
    ('Клубника', 'Многолетняя, любит солнце.', 10, 25, 60, 4, 5),
]


class Command(BaseCommand):
    help = 'Заполняет БД начальными данными: регионы и культуры.'

    def handle(self, *args, **options):
        for name, lat, lon, zone, soil in REGIONS:
            Region.objects.get_or_create(
                name=name,
                defaults={
                    'latitude': lat,
                    'longitude': lon,
                    'climate_zone': zone,
                    'soil_type': soil,
                },
            )
        for name, desc, t_min, t_max, days, m_start, m_end in CULTURES:
            Culture.objects.update_or_create(
                name=name,
                defaults={
                    'description': desc,
                    'min_planting_temp': t_min,
                    'max_planting_temp': t_max,
                    'vegetation_days': days,
                    'planting_month_start': m_start,
                    'planting_month_end': m_end,
                },
            )
        self.stdout.write(self.style.SUCCESS(
            f'Загружено: {Region.objects.count()} регионов, {Culture.objects.count()} культур'
        ))