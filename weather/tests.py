from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from weather.forms import GardenPlotForm, PlantingForm
from weather.models import Region, Culture, WeatherRecord, GardenPlot, Planting
from weather.services.recommendation_engine import generate_for_plot


class ModelTests(TestCase):
    def setUp(self):
        self.region = Region.objects.create(
            name='Тестовая область', latitude=55.0, longitude=37.0,
            climate_zone='central', soil_type='clay',
        )
        self.culture = Culture.objects.create(
            name='Тесттомат', description='теплолюбивая', min_planting_temp=15,
            max_planting_temp=30, vegetation_days=100,
            planting_month_start=5, planting_month_end=6,
        )

    def test_weather_record_frost_risk(self):
        rec = WeatherRecord(region=self.region, date=date(2026, 6, 1),
                            temp_min=2, temp_max=10, humidity=70, precipitation=0)
        self.assertTrue(rec.is_frost_risk)

    def test_weather_record_no_frost(self):
        rec = WeatherRecord(region=self.region, date=date(2026, 6, 1),
                            temp_min=8, temp_max=20, humidity=70, precipitation=0)
        self.assertFalse(rec.is_frost_risk)

    def test_temp_avg(self):
        rec = WeatherRecord(region=self.region, date=date(2026, 6, 1),
                            temp_min=10, temp_max=20, humidity=70, precipitation=0)
        self.assertEqual(rec.temp_avg, 15)

    def test_is_planting_season_inside(self):
        self.assertTrue(self.culture.is_planting_season(date(2026, 5, 15)))

    def test_is_planting_season_outside(self):
        self.assertFalse(self.culture.is_planting_season(date(2026, 9, 15)))

    def test_planting_window_display(self):
        self.assertEqual(self.culture.planting_window_display, 'май–июнь')


class PlantingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('gardener', password='pass12345')
        self.region = Region.objects.create(
            name='Юг', latitude=45.0, longitude=39.0,
            climate_zone='south', soil_type='chernozem',
        )
        self.culture = Culture.objects.create(
            name='Тесткартофель', description='универсальная', min_planting_temp=8,
            max_planting_temp=25, vegetation_days=90,
            planting_month_start=4, planting_month_end=5,
        )
        self.plot = GardenPlot.objects.create(
            user=self.user, region=self.region, name='Дача',
            area=6, soil_type='chernozem',
        )

    def test_expected_harvest_for_planted(self):
        planting = Planting.objects.create(
            plot=self.plot, culture=self.culture,
            status=Planting.Status.PLANTED, planted_date=date(2026, 5, 1),
        )
        self.assertEqual(planting.expected_harvest, date(2026, 5, 1) + timedelta(days=90))

    def test_expected_harvest_none_for_planned(self):
        planting = Planting.objects.create(
            plot=self.plot, culture=self.culture, status=Planting.Status.PLANNED,
        )
        self.assertIsNone(planting.expected_harvest)


class RecommendationEngineTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('farmer', password='pass12345')
        self.region = Region.objects.create(
            name='Жаркий край', latitude=45.0, longitude=39.0,
            climate_zone='south', soil_type='sandy',
        )
        self.culture = Culture.objects.create(
            name='Тестогурец', description='теплолюбивый', min_planting_temp=18,
            max_planting_temp=32, vegetation_days=60,
            planting_month_start=1, planting_month_end=12,
        )
        self.plot = GardenPlot.objects.create(
            user=self.user, region=self.region, name='Грядка',
            area=4, soil_type='sandy',
        )
        today = timezone.now().date()
        WeatherRecord.objects.create(
            region=self.region, date=today + timedelta(days=1),
            temp_min=1, temp_max=8, humidity=70, precipitation=0,
        )

    def test_frost_recommendation_created_for_planted(self):
        Planting.objects.create(
            plot=self.plot, culture=self.culture,
            status=Planting.Status.PLANTED, planted_date=timezone.now().date(),
        )
        generate_for_plot(self.plot)
        texts = [r.text for r in self.plot.recommendations.all()]
        self.assertTrue(any('заморозк' in t.lower() for t in texts))

    def test_generate_is_idempotent(self):
        Planting.objects.create(
            plot=self.plot, culture=self.culture,
            status=Planting.Status.PLANTED, planted_date=timezone.now().date(),
        )
        generate_for_plot(self.plot)
        first = self.plot.recommendations.count()
        generate_for_plot(self.plot)
        second = self.plot.recommendations.count()
        self.assertEqual(first, second)


class FormTests(TestCase):
    def setUp(self):
        self.region = Region.objects.create(
            name='Регион', latitude=55.0, longitude=37.0,
            climate_zone='central', soil_type='loam',
        )

    def test_plot_form_rejects_negative_area(self):
        form = GardenPlotForm(data={
            'name': 'Участок', 'region': self.region.id,
            'soil_type': 'loam', 'area': -5,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('area', form.errors)

    def test_plot_form_valid(self):
        form = GardenPlotForm(data={
            'name': 'Участок', 'region': self.region.id,
            'soil_type': 'loam', 'area': 6,
        })
        self.assertTrue(form.is_valid())