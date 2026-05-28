import os
from datetime import date
import requests

OWM_URL = 'https://api.openweathermap.org/data/2.5/forecast'


def fetch_forecast(region):
    """Возвращает список словарей с прогнозом на 5 дней по региону."""
    api_key = os.getenv('OWM_API_KEY')
    if not api_key:
        raise RuntimeError('OWM_API_KEY не задан в .env')

    params = {
        'lat': float(region.latitude),
        'lon': float(region.longitude),
        'appid': api_key,
        'units': 'metric',
        'lang': 'ru',
    }
    response = requests.get(OWM_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json().get('list', [])


def aggregate_daily(forecast_items):
    """Сворачивает 3-часовые срезы в дневные min/max/влажность/осадки."""
    by_date = {}
    for item in forecast_items:
        day = date.fromtimestamp(item['dt'])
        slot = by_date.setdefault(day, {'temps': [], 'humidity': [], 'rain': 0})
        slot['temps'].append(item['main']['temp'])
        slot['humidity'].append(item['main']['humidity'])
        slot['rain'] += item.get('rain', {}).get('3h', 0)

    result = []
    for day, data in by_date.items():
        result.append({
            'date': day,
            'temp_min': min(data['temps']),
            'temp_max': max(data['temps']),
            'humidity': sum(data['humidity']) // len(data['humidity']),
            'precipitation': data['rain'],
        })
    return result