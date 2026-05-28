from datetime import timedelta
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Culture, Region, WeatherRecord


def culture_list(request):
    query = request.GET.get('q', '').strip()
    cultures = Culture.objects.all().order_by('name')
    if query:
        cultures = cultures.filter(name__icontains=query)
    return render(request, 'weather/culture_list.html', {'cultures': cultures})


def culture_detail(request, pk):
    culture = get_object_or_404(Culture, pk=pk)
    return render(request, 'weather/culture_detail.html', {'culture': culture})


def region_list(request):
    regions = Region.objects.all().order_by('name')
    return render(request, 'weather/region_list.html', {'regions': regions})


def region_detail(request, pk):
    region = get_object_or_404(Region, pk=pk)
    since = timezone.now().date() - timedelta(days=30)
    records = WeatherRecord.objects.filter(region=region, date__gte=since).order_by('-date')
    return render(request, 'weather/region_detail.html', {'region': region, 'records': records})