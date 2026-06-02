from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

MONTHS_RU = ('', 'январь', 'февраль', 'март', 'апрель', 'май', 'июнь',
             'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь')


class Region(models.Model):
    CLIMATE_ZONES = [
        ('north', 'Северный'),
        ('central', 'Центральный'),
        ('south', 'Южный'),
    ]
    SOIL_TYPES = [
        ('chernozem', 'Чернозём'),
        ('loam', 'Суглинок'),
        ('sandy', 'Песчаная'),
        ('clay', 'Глинистая'),
        ('podzolic', 'Дерново-подзолистая'),
    ]

    name = models.CharField('Название', max_length=100, unique=True)
    latitude = models.FloatField('Широта')
    longitude = models.FloatField('Долгота')
    climate_zone = models.CharField('Климатическая зона', max_length=20, choices=CLIMATE_ZONES)
    soil_type = models.CharField('Тип почвы', max_length=20, choices=SOIL_TYPES, default='loam')

    class Meta:
        ordering = ['name']
        verbose_name = 'Регион'
        verbose_name_plural = 'Регионы'

    def __str__(self):
        return self.name


class Culture(models.Model):
    name = models.CharField('Название', max_length=100, unique=True)
    description = models.TextField('Описание')
    min_planting_temp = models.FloatField('Мин. температура посадки')
    max_planting_temp = models.FloatField('Макс. температура посадки')
    vegetation_days = models.PositiveIntegerField('Дней вегетации')
    planting_month_start = models.PositiveSmallIntegerField(
        'Начало посадки (месяц)', default=4,
        validators=[MinValueValidator(1), MaxValueValidator(12)])
    planting_month_end = models.PositiveSmallIntegerField(
        'Конец посадки (месяц)', default=5,
        validators=[MinValueValidator(1), MaxValueValidator(12)])
    image = models.ImageField('Фото', upload_to='cultures/', blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Культура'
        verbose_name_plural = 'Культуры'

    def __str__(self):
        return self.name

    def is_planting_season(self, on_date):
        m = on_date.month
        start, end = self.planting_month_start, self.planting_month_end
        if start <= end:
            return start <= m <= end
        return m >= start or m <= end  # окно через Новый год (напр. ноябрь–февраль)

    @property
    def planting_window_display(self):
        return f'{MONTHS_RU[self.planting_month_start]}–{MONTHS_RU[self.planting_month_end]}'


class WeatherRecord(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='weather_records')
    date = models.DateField('Дата')
    temp_min = models.FloatField('Мин. температура')
    temp_max = models.FloatField('Макс. температура')
    humidity = models.PositiveSmallIntegerField('Влажность, %')
    precipitation = models.FloatField('Осадки, мм', default=0)

    class Meta:
        ordering = ['-date']
        unique_together = ('region', 'date')
        verbose_name = 'Запись погоды'
        verbose_name_plural = 'Записи погоды'

    @property
    def temp_avg(self):
        return (self.temp_min + self.temp_max) / 2

    @property
    def is_frost_risk(self):
        return self.temp_min < 3

    def __str__(self):
        return f'{self.region.name} - {self.date}'


class GardenPlot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='plots')
    region = models.ForeignKey(Region, on_delete=models.PROTECT, related_name='plots')
    cultures = models.ManyToManyField(Culture, through='Planting', related_name='plots', blank=True)
    name = models.CharField('Название участка', max_length=100)
    area = models.FloatField('Площадь, сот.')
    soil_type = models.CharField('Тип почвы на участке', max_length=20,
                                 choices=Region.SOIL_TYPES, default='loam')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Участок'
        verbose_name_plural = 'Участки'

    def __str__(self):
        return f'{self.name} ({self.user.username})'


class Planting(models.Model):
    class Status(models.TextChoices):
        PLANNED = 'planned', 'Планируется'
        PLANTED = 'planted', 'Посажено'

    plot = models.ForeignKey(GardenPlot, on_delete=models.CASCADE, related_name='plantings')
    culture = models.ForeignKey(Culture, on_delete=models.CASCADE, related_name='plantings')
    status = models.CharField('Статус', max_length=20,
                              choices=Status.choices, default=Status.PLANNED)
    planted_date = models.DateField('Дата посадки', null=True, blank=True)

    class Meta:
        unique_together = ('plot', 'culture')
        verbose_name = 'Посадка'
        verbose_name_plural = 'Посадки'

    @property
    def expected_harvest(self):
        if self.status == self.Status.PLANTED and self.planted_date:
            return self.planted_date + timedelta(days=self.culture.vegetation_days)
        return None

    def __str__(self):
        return f'{self.culture.name} — {self.plot.name} ({self.get_status_display()})'


class Recommendation(models.Model):
    PRIORITIES = [
        (1, 'Низкий'),
        (2, 'Средний'),
        (3, 'Высокий'),
    ]

    plot = models.ForeignKey(GardenPlot, on_delete=models.CASCADE, related_name='recommendations')
    culture = models.ForeignKey(Culture, on_delete=models.CASCADE)
    text = models.TextField('Рекомендация')
    priority = models.PositiveSmallIntegerField('Приоритет', choices=PRIORITIES, default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-priority', '-created_at']
        verbose_name = 'Рекомендация'
        verbose_name_plural = 'Рекомендации'

    def __str__(self):
        return f'[{self.get_priority_display()}] {self.text[:50]}'