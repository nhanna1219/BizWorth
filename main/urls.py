from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('home/', views.home),
    path('get_ticker_chart/', views.get_ticker_chart, name='get_ticker_chart'),
]
