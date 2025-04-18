from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import *

urlpatterns = [
    
    path('weekly/', views.WeeklyReportView.as_view()),
    path('monthly/', views.MonthlyReportView.as_view()),
    
    path('chart/summary/', views.MonthlySummaryChartView.as_view()),

    path('payment-summary/weekly/', UserPaymentSummaryWeeklyListView.as_view(), name='payment-summary-weekly'),
    path('payment-summary/monthly/', UserPaymentSummaryMonthlyListView.as_view(), name='payment-summary-monthly'),
]
