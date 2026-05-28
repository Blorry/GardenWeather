from django.urls import path
from . import views

urlpatterns = [
    path('', views.culture_list, name='culture_list'),
    path('culture/<int:pk>/', views.culture_detail, name='culture_detail'),
    path('regions/', views.region_list, name='region_list'),
    path('region/<int:pk>/', views.region_detail, name='region_detail'),
]