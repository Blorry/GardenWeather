from datetime import timedelta

from django.utils import timezone

from weather.models import Recommendation, WeatherRecord


def generate_for_plot(plot):
    """Создаёт сгруппированные рекомендации для участка на ближайшие 7 дней."""
    today = timezone.now().date()
    horizon = today + timedelta(days=7)
    records = list(
        WeatherRecord.objects
        .filter(region=plot.region, date__gte=today, date__lte=horizon)
        .order_by('date')
    )
    if not records:
        return 0

    created = 0
    for culture in plot.cultures.all():
        for text, priority in _build_suggestions(culture, records):
            _, was_created = Recommendation.objects.get_or_create(
                plot=plot, culture=culture, text=text,
                defaults={'priority': priority},
            )
            if was_created:
                created += 1
    return created


def _build_suggestions(culture, records):
    """Возвращает список (text, priority): не более одной рекомендации каждого типа."""
    suggestions = []

    # 1. Заморозки — критично, перечисляем все даты
    frost = [r.date for r in records if r.is_frost_risk]
    if frost:
        suggestions.append((
            f'Ночные заморозки ожидаются {_dates(frost)} — '
            f'укройте {culture.name.lower()} от холода.',
            3,
        ))

    # 2. Благоприятная температура для посадки — одна рекомендация на диапазон
    favorable = [
        r for r in records
        if culture.min_planting_temp <= r.temp_min
        and r.temp_max <= culture.max_planting_temp
        and not r.is_frost_risk
    ]
    if favorable:
        suggestions.append((
            f'{_range(favorable)}: благоприятная температура для посадки культуры «{culture.name}».',
            2,
        ))

    # 3. Жара и сухо — одна рекомендация на диапазон
    hot_dry = [r for r in records if r.precipitation < 1 and r.temp_max > 25]
    if hot_dry:
        suggestions.append((
            f'{_range(hot_dry)}: жарко и сухо — '
            f'обеспечьте регулярный полив для культуры «{culture.name}».',
            2,
        ))

    # 4. Обильные осадки — перечисляем даты
    rainy = [r.date for r in records if r.precipitation > 10]
    if rainy:
        suggestions.append((
            f'Обильные осадки ожидаются {_dates(rainy)} — '
            f'дополнительный полив культуры «{culture.name}» не требуется.',
            1,
        ))

    return suggestions


def _dates(date_list):
    """Преобразует список дат в строку '03.06, 05.06, 07.06'."""
    return ', '.join(d.strftime('%d.%m') for d in date_list)


def _range(records):
    """Возвращает 'DD.MM' или 'с DD.MM по DD.MM' для списка записей."""
    if len(records) == 1:
        return records[0].date.strftime('%d.%m')
    return f'С {records[0].date.strftime("%d.%m")} по {records[-1].date.strftime("%d.%m")}'