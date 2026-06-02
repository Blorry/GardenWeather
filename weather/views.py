from datetime import timedelta

import plotly.express as px
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .forms import GardenPlotForm, PlantingForm
from .models import Culture, Region, WeatherRecord, GardenPlot, Planting
from .services.analytics import to_dataframe, region_stats


# ---------- Каталог культур ----------

def culture_list(request):
    query = request.GET.get('q', '').strip()
    cultures = Culture.objects.all()
    if query:
        cultures = cultures.filter(name__icontains=query)
    return render(request, 'weather/culture_list.html', {'cultures': cultures})


def culture_detail(request, pk):
    culture = get_object_or_404(Culture, pk=pk)
    return render(request, 'weather/culture_detail.html', {'culture': culture})


# ---------- Регионы и погода ----------

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
        legend_names = {
            'temp_min': 'Мин. температура',
            'temp_max': 'Макс. температура',
            'rolling_avg': 'Скользящее среднее',
        }
        fig.for_each_trace(lambda t: t.update(name=legend_names[t.name]))
        fig.update_layout(template='plotly_white', height=400)
        fig.update_xaxes(tickformat='%d.%m', dtick='D1')
        chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    stats = region_stats(records)
    return render(request, 'weather/region_detail.html', {
        'region': region, 'records': records,
        'chart_html': chart_html, 'stats': stats,
    })


# ---------- Личный кабинет: участки ----------

@login_required
def plot_list(request):
    plots = (GardenPlot.objects
             .filter(user=request.user)
             .select_related('region')
             .prefetch_related('cultures')
             .annotate(rec_count=Count('recommendations')))
    return render(request, 'weather/plot_list.html', {'plots': plots})


@login_required
def plot_detail(request, pk):
    plot = get_object_or_404(GardenPlot, pk=pk, user=request.user)

    if request.method == 'POST':
        form = PlantingForm(request.POST)
        if form.is_valid():
            culture = form.cleaned_data['culture']
            if not Planting.objects.filter(plot=plot, culture=culture).exists():
                planting = form.save(commit=False)
                planting.plot = plot
                planting.save()
            return redirect('plot_detail', pk=plot.pk)
    else:
        form = PlantingForm()

    plantings = plot.plantings.select_related('culture')
    recommendations = plot.recommendations.select_related('culture').order_by('-priority', '-created_at')
    return render(request, 'weather/plot_detail.html', {
        'plot': plot,
        'plantings': plantings,
        'recommendations': recommendations,
        'form': form,
    })


@login_required
def plot_create(request):
    if request.method == 'POST':
        form = GardenPlotForm(request.POST)
        if form.is_valid():
            plot = form.save(commit=False)
            plot.user = request.user
            plot.save()
            form.save_m2m()
            return redirect('plot_list')
    else:
        form = GardenPlotForm()
    return render(request, 'weather/plot_form.html', {'form': form, 'title': 'Новый участок'})


@login_required
def plot_edit(request, pk):
    plot = get_object_or_404(GardenPlot, pk=pk, user=request.user)
    form = GardenPlotForm(request.POST or None, instance=plot)
    if form.is_valid():
        form.save()
        return redirect('plot_list')
    return render(request, 'weather/plot_form.html', {'form': form, 'title': 'Редактирование участка'})


@login_required
def plot_delete(request, pk):
    plot = get_object_or_404(GardenPlot, pk=pk, user=request.user)
    if request.method == 'POST':
        plot.delete()
        return redirect('plot_list')
    return render(request, 'weather/plot_confirm_delete.html', {'plot': plot})


# ---------- Подтверждение выхода ----------

def logout_confirm(request):
    return render(request, 'registration/logout_confirm.html')

@login_required
def planting_toggle(request, pk):
    planting = get_object_or_404(Planting, pk=pk, plot__user=request.user)
    if request.method == 'POST':
        if planting.status == Planting.Status.PLANNED:
            planting.status = Planting.Status.PLANTED
            planting.planted_date = timezone.now().date()
        else:
            planting.status = Planting.Status.PLANNED
            planting.planted_date = None
        planting.save()
    return redirect('plot_detail', pk=planting.plot.pk)


@login_required
def planting_delete(request, pk):
    planting = get_object_or_404(Planting, pk=pk, plot__user=request.user)
    plot_pk = planting.plot.pk
    if request.method == 'POST':
        planting.delete()
    return redirect('plot_detail', pk=plot_pk)