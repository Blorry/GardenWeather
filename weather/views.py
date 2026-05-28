from datetime import timedelta
import plotly.express as px
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Culture, Region, WeatherRecord
from .services.analytics import to_dataframe, region_stats


def culture_list(request):
    query = request.GET.get('q', '').strip()
    cultures = Culture.objects.all()
    if query:
        cultures = cultures.filter(name__icontains=query)
    return render(request, 'weather/culture_list.html', {'cultures': cultures})


def culture_detail(request, pk):
    culture = get_object_or_404(Culture, pk=pk)
    return render(request, 'weather/culture_detail.html', {'culture': culture})


def region_list(request):
    regions = Region.objects.all()
    return render(request, 'weather/region_list.html', {'regions': regions})


def region_detail(request, pk):
    region = get_object_or_404(Region, pk=pk)
    since = timezone.now().date() - timedelta(days=30)
    records = WeatherRecord.objects.filter(region=region, date__gte=since).order_by('date')

    df = to_dataframe(records)
    chart_html = ''
    if not df.empty:
        fig = px.line(
            df, x='date', y=['temp_min', 'temp_max', 'rolling_avg'],
            labels={'value': '°C', 'date': 'Дата', 'variable': 'Показатель'},
            title=f'Температура: {region.name}',
        )
        fig.update_layout(template='plotly_white', height=400)
        chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    stats = region_stats(records)
    return render(request, 'weather/region_detail.html', {
        'region': region, 'records': records,
        'chart_html': chart_html, 'stats': stats,
    })