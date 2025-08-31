from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('wind/', views.wind, name='wind'),
    path('flow_rate/', views.flow_rate, name='flow_rate'),
]