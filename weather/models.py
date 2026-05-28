from django.db import models
from django.contrib.auth.models import User


class Region(models.Model):
    CLIMATE_ZONES = [
        ('north', 'Северный'),
        ('central', 'Центральный'),
        ('south', 'Южный'),
    ]

    name = models.CharField('Название', max_length=100, unique=True)
    latitude = models.FloatField('Широта')
    longitude = models.FloatField('Долгота')
    climate_zone = models.CharField('Климатическая зона', max_length=20, choices=CLIMATE_ZONES)

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
    image = models.ImageField('Фото', upload_to='cultures/', blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Культура'
        verbose_name_plural = 'Культуры'

    def __str__(self):
        return self.name


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
    cultures = models.ManyToManyField(Culture, related_name='plots', blank=True)
    name = models.CharField('Название участка', max_length=100)
    area = models.FloatField('Площадь, сот.')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Участок'
        verbose_name_plural = 'Участки'

    def __str__(self):
        return f'{self.name} ({self.user.username})'


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