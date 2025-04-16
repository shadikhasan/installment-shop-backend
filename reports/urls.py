from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import *

urlpatterns = [
    
    path('weekly/', views.WeeklyReportView.as_view()),
    path('monthly/', views.MonthlyReportView.as_view()),

]
