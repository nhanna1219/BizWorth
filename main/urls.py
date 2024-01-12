from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('home/', views.home),
    path('get_ticker_chart/', views.get_ticker_chart, name='get_ticker_chart'),
    path('update_canslim_point/', views.update_canslim_point, name='update_canslim_point'),
    path('update_mx4_point/', views.update_mx4_point, name='update_mx4_point'),
    path('get_business_info/', views.get_business_info, name='get_business_info')
    # path('get_ticker_chart/', views.get_ticker_chart, name='get_ticker_chart'),
]
