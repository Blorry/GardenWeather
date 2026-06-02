from django.urls import path
from . import views

urlpatterns = [
    path('', views.culture_list, name='culture_list'),
    path('culture/<int:pk>/', views.culture_detail, name='culture_detail'),
    path('regions/', views.region_list, name='region_list'),
    path('region/<int:pk>/', views.region_detail, name='region_detail'),
    path('plots/', views.plot_list, name='plot_list'),
    path('plots/new/', views.plot_create, name='plot_create'),
    path('plots/<int:pk>/edit/', views.plot_edit, name='plot_edit'),
    path('plots/<int:pk>/delete/', views.plot_delete, name='plot_delete'),
    path('accounts/logout-confirm/', views.logout_confirm, name='logout_confirm'),
    path('plots/<int:pk>/', views.plot_detail, name='plot_detail'),
]