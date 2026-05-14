# Техническое задание: GardenWeather

## 1. Цель проекта
Сервис мониторинга погодных условий для дачников. По геолокации участка
сервис получает прогноз погоды через внешнее API (OpenWeatherMap),
сопоставляет его с условиями посадки культур и формирует рекомендации
по уходу (полив, укрытие от заморозков, время посадки).

## 2. Роли пользователей
- **Гость** — каталог культур, графики погоды по регионам.
- **Зарегистрированный пользователь** — создание участков, добавление культур, личные рекомендации.
- **Администратор** — управление справочниками через админ-панель.

## 3. Модели данных
1. **Region** — регион/город (name, latitude, longitude, climate_zone).
2. **Culture** — культура (name, slug, description, min/max_planting_temp, vegetation_days, image).
3. **WeatherRecord** — запись погоды (region FK, date, temp_min/max, humidity, precipitation).
4. **GardenPlot** — участок (user FK, region FK, cultures M2M, name, area).
5. **Recommendation** — рекомендация (plot FK, culture FK, text, priority, created_at).

## 4. Ключевой функционал
- Каталог культур с поиском и фильтрацией по климатической зоне.
- График температур и осадков за 30 дней (Plotly) на странице региона.
- Личный кабинет: добавление участка, выбор культур, лента рекомендаций.
- Команда `fetch_weather` — забор данных из OpenWeatherMap.
- Команда `generate_recommendations` — генерация советов по прогнозу.

## 5. Технический стек
- Backend: Python 3.14, Django 5.0
- DB: SQLite (dev), PostgreSQL (опционально prod)
- Аналитика: Pandas (агрегации температур), Plotly (графики)
- API: OpenWeatherMap (requests)
- Frontend: Bootstrap 5, шаблоны Django с наследованием
- Deploy: PythonAnywhere

## Изменения в ходе реализации
(заполняется по мере отклонений от плана)