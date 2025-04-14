from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.ProductListView.as_view()),

    path('purchases/', views.PurchaseListView.as_view()),
    path('purchases/my/', views.MyPurchaseListView.as_view()),
    path('purchases/create/', views.PurchaseCreateView.as_view()),

    path('installments/', views.InstallmentListView.as_view()),
    path('installments/my/', views.MyInstallmentListView.as_view()),
    path('installments/<int:pk>/pay/', views.InstallmentPayView.as_view()),

    path('reports/weekly/', views.WeeklyReportView.as_view()),
    path('reports/monthly/', views.MonthlyReportView.as_view()),
]
