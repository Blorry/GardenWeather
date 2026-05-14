from django.db import models
from django.contrib.auth.models import User


class Region(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    climate_zone = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Culture(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    min_planting_temp = models.FloatField()
    max_planting_temp = models.FloatField()
    vegetation_days = models.IntegerField()
    image = models.ImageField(upload_to='cultures/', blank=True)

    def __str__(self):
        return self.name


class WeatherRecord(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    date = models.DateField()
    temp_min = models.FloatField()
    temp_max = models.FloatField()
    humidity = models.IntegerField()
    precipitation = models.FloatField()

    def __str__(self):
        return f'{self.region} {self.date}'


class GardenPlot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    cultures = models.ManyToManyField(Culture)
    name = models.CharField(max_length=100)
    area = models.FloatField()

    def __str__(self):
        return self.name


class Recommendation(models.Model):
    plot = models.ForeignKey(GardenPlot, on_delete=models.CASCADE)
    culture = models.ForeignKey(Culture, on_delete=models.CASCADE)
    text = models.TextField()
    priority = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:50]