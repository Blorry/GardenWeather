from django.contrib import admin
from .models import Region, Culture, WeatherRecord, GardenPlot, Recommendation, Planting

class PlantingInline(admin.TabularInline):
    model = Planting
    extra = 1

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'climate_zone', 'soil_type', 'latitude', 'longitude')
    list_filter = ('climate_zone', 'soil_type')
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
    inlines = [PlantingInline]


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('plot', 'culture', 'priority', 'created_at')
    list_filter = ('priority', 'created_at')

@admin.register(Planting)
class PlantingAdmin(admin.ModelAdmin):
    list_display = ('culture', 'plot', 'status', 'planted_date')
    list_filter = ('status',)
    search_fields = ('culture__name', 'plot__name')