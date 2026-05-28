import pandas as pd
from django.db.models import Avg


def region_stats(weather_qs):
    """Сводка по QuerySet записей погоды."""
    agg = weather_qs.aggregate(
        avg_min=Avg('temp_min'),
        avg_max=Avg('temp_max'),
        total_rain=Avg('precipitation'),
    )
    return {k: round(v, 1) if v is not None else 0 for k, v in agg.items()}


def to_dataframe(weather_qs):
    """Превращает QuerySet в Pandas DataFrame для графиков."""
    rows = list(weather_qs.values('date', 'temp_min', 'temp_max', 'precipitation', 'humidity'))
    df = pd.DataFrame(rows)
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        df['temp_avg'] = (df['temp_min'] + df['temp_max']) / 2
        df['rolling_avg'] = df['temp_avg'].rolling(window=3, min_periods=1).mean()
    return df