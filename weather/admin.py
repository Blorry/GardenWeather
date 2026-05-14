from django.contrib import admin
from .models import Region, Culture, WeatherRecord, GardenPlot, Recommendation


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'climate_zone', 'latitude', 'longitude')
    search_fields = ('name',)


@admin.register(Culture)
class CultureAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_planting_temp', 'max_planting_temp', 'vegetation_days')
    search_fields = ('name',)


@admin.register(WeatherRecord)
class WeatherRecordAdmin(admin.ModelAdmin):
    list_display = ('region', 'date', 'temp_min', 'temp_max', 'precipitation')
    list_filter = ('region', 'date')


@admin.register(GardenPlot)
class GardenPlotAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'region', 'area')
    search_fields = ('name', 'user__username')


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('plot', 'culture', 'priority', 'created_at')
    list_filter = ('priority', 'created_at')