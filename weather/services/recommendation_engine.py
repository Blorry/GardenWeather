from datetime import timedelta

from django.utils import timezone

from weather.models import Recommendation, WeatherRecord

# Профили почв: пороги полива и агрономический совет
SOIL_PROFILES = {
    'sandy': {
        'hot': 22, 'dry': 2.0,
        'note': 'Песчаная почва быстро теряет влагу — поливайте чаще, малыми порциями.',
    },
    'loam': {
        'hot': 25, 'dry': 1.0,
        'note': '',
    },
    'clay': {
        'hot': 28, 'dry': 1.0,
        'note': 'Глинистая почва долго удерживает воду — поливайте реже, но обильно.',
    },
    'chernozem': {
        'hot': 26, 'dry': 1.0,
        'note': 'После полива рыхлите чернозём, чтобы не образовалась корка.',
    },
    'podzolic': {
        'hot': 24, 'dry': 1.5,
        'note': 'Дерново-подзолистая почва бедна и кисла — вносите органику и не допускайте пересыхания.',
    },
}
DEFAULT_PROFILE = {'hot': 25, 'dry': 1.0, 'note': ''}


def generate_for_plot(plot):
    """Создаёт рекомендации для участка с учётом почвы и статуса посадок."""
    plot.recommendations.all().delete()  # убираем устаревшие — генерируем заново
    today = timezone.now().date()
    horizon = today + timedelta(days=7)
    records = list(
        WeatherRecord.objects
        .filter(region=plot.region, date__gte=today, date__lte=horizon)
        .order_by('date')
    )
    if not records:
        return 0

    profile = SOIL_PROFILES.get(plot.soil_type, DEFAULT_PROFILE)
    created = 0
    for planting in plot.plantings.select_related('culture'):
        is_planted = planting.status == 'planted'
        harvest_date = planting.expected_harvest if is_planted else None
        for text, priority in _build_suggestions(planting.culture, records, profile, is_planted, harvest_date):
            _, was_created = Recommendation.objects.get_or_create(
                plot=plot, culture=planting.culture, text=text,
                defaults={'priority': priority},
            )
            if was_created:
                created += 1
    return created


def _build_suggestions(culture, records, profile, is_planted, harvest_date=None):
    """Планируется -> о посадке; посажено -> уход только до сбора урожая."""
    suggestions = []
    name = culture.name

    if is_planted:
        # Урожай созревает в пределах прогноза -> напоминаем о сборе
        if harvest_date and harvest_date <= records[-1].date:
            suggestions.append((
                f'Урожай культуры «{name}» созревает примерно {harvest_date:%d.%m} — планируйте сбор.', 2,
            ))

        # Уход актуален только до дня сбора
        active = [r for r in records if harvest_date is None or r.date < harvest_date]
        if not active:
            return suggestions  # сезон вегетации завершён — уход не нужен

        frost = [r.date for r in active if r.is_frost_risk]
        if frost:
            suggestions.append((
                f'Ночные заморозки {_dates(frost)} — укройте посадки культуры «{name}».', 3,
            ))

        hot_dry = [
            r for r in active
            if r.precipitation < profile['dry'] and r.temp_max > profile['hot']
        ]
        if hot_dry:
            text = f'{_range(hot_dry)}: жарко и сухо — полейте посадки культуры «{name}».'
            if profile['note']:
                text += f' {profile["note"]}'
            suggestions.append((text, 2))

        rainy = [r.date for r in active if r.precipitation > 10]
        if rainy:
            suggestions.append((
                f'Обильные осадки {_dates(rainy)} — полив культуры «{name}» не требуется.', 1,
            ))
    else:
        # Культура планируется -> заморозки как помеха + сезон + температура
        frost = [r.date for r in records if r.is_frost_risk]
        if frost:
            suggestions.append((
                f'Ночные заморозки {_dates(frost)} — отложите посадку культуры «{name}» '
                f'или подготовьте укрытие.', 3,
            ))

        in_season = any(culture.is_planting_season(r.date) for r in records)
        if not in_season:
            suggestions.append((
                f'Сейчас не сезон для посадки культуры «{name}» '
                f'(оптимальные сроки: {culture.planting_window_display}).', 1,
            ))
        else:
            favorable = [
                r for r in records
                if culture.is_planting_season(r.date)
                and culture.min_planting_temp <= r.temp_min
                and r.temp_max <= culture.max_planting_temp
                and not r.is_frost_risk
            ]
            if favorable:
                suggestions.append((
                    f'{_range(favorable)}: благоприятная температура для посадки культуры «{name}».', 2,
                ))

    return suggestions


def _dates(date_list):
    """Список дат в строку '03.06, 05.06'."""
    return ', '.join(d.strftime('%d.%m') for d in date_list)


def _range(records):
    """'DD.MM' или 'С DD.MM по DD.MM' для списка записей."""
    if len(records) == 1:
        return records[0].date.strftime('%d.%m')
    return f'С {records[0].date.strftime("%d.%m")} по {records[-1].date.strftime("%d.%m")}'