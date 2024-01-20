from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('home/', views.home),
    path('read_all_csv/', views.read_all_csv, name='read_all_csv'),
path('get_ticker_chart/', views.get_ticker_chart, name='get_ticker_chart'),
    path('update_canslim_point/', views.update_canslim_point, name='update_canslim_point'),
    path('update_mx4_point/', views.update_mx4_point, name='update_mx4_point'),
    path('get_business_info/', views.get_business_info, name='get_business_info'),
    path('get_financial_report/', views.get_financial_report, name='get_financial_report'),
    path('get_rate_table/', views.get_rate_table, name='get_rate_table'),
    path('filter_data_tbl/', views.filter_data_tbl, name='filter_data_tbl'),
    path('get_balance_sheet/', views.get_balance_sheet, name='get_balance_sheet'),
    path('filter_balance_sheet/', views.filter_balance_sheet, name='filter_balance_sheet'),
    path('get_operation_result/', views.get_operation_result, name='get_operation_result'),
    path('filter_operation_result/', views.filter_operation_result, name='filter_operation_result'),
    path('get_financial_fig/', views.get_financial_fig, name='get_financial_fig'),
    path('filter_financial_fig/', views.filter_financial_fig, name='filter_financial_fig')
    
    
    # path('get_ticker_chart/', views.get_ticker_chart, name='get_ticker_chart'),
]
