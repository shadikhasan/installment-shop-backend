from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Purchase, Installment, Product
from .serializers import (
    PurchaseSerializer, InstallmentSerializer,
    InstallmentPaySerializer, ProductSerializer
)
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from datetime import timedelta


class ProductListView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]


class PurchaseCreateView(generics.CreateAPIView):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class PurchaseListView(generics.ListAPIView):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    permission_classes = [permissions.IsAdminUser]


class MyPurchaseListView(generics.ListAPIView):
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Purchase.objects.filter(customer=self.request.user)


class InstallmentListView(generics.ListAPIView):
    queryset = Installment.objects.all()
    serializer_class = InstallmentSerializer
    permission_classes = [permissions.IsAdminUser]


class MyInstallmentListView(generics.ListAPIView):
    serializer_class = InstallmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Installment.objects.filter(purchase__customer=self.request.user)


class InstallmentPayView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            installment = Installment.objects.get(pk=pk, purchase__customer=request.user)
        except Installment.DoesNotExist:
            return Response({'error': 'Installment not found'}, status=404)

        serializer = InstallmentPaySerializer(data=request.data)
        if serializer.is_valid():
            installment.paid_amount += serializer.validated_data['paid_amount']
            installment.save()
            return Response({'status': 'Payment updated'})
        return Response(serializer.errors, status=400)


class WeeklyReportView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        start = timezone.now() - timedelta(days=7)
        data = Installment.objects.filter(payment_date__gte=start).aggregate(
            total_paid=Sum('paid_amount'),
            total_due=Sum('due_amount')
        )
        return Response(data)


class MonthlyReportView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        start = timezone.now() - timedelta(days=30)
        data = Installment.objects.filter(payment_date__gte=start).aggregate(
            total_paid=Sum('paid_amount'),
            total_due=Sum('due_amount')
        )
        return Response(data)
