from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from .models import Purchase, Installment, Product
from rest_framework.exceptions import PermissionDenied
from .serializers import *
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from datetime import timedelta
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from decimal import Decimal
from django.utils import timezone
from .models import Installment
from .serializers import *


from rest_framework.exceptions import NotAuthenticated

from rest_framework.exceptions import PermissionDenied, ValidationError



class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]  # Any user can view products
        return [permissions.IsAdminUser()]  # Only admins can create, update, or delete products

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


class PayInstallmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, installment_id):
        user = request.user
        installment = Installment.objects.filter(id=installment_id, purchase__customer=user, status='due').first()

        if not installment:
            return Response({"detail": "Installment not found or already paid."}, status=status.HTTP_404_NOT_FOUND)

        # Pass the installment to the serializer context
        serializer = PayInstallmentSerializer(data=request.data, context={'installment': installment})

        if serializer.is_valid():
            # Apply payment logic here
            amount = serializer.validated_data['amount']
            installment.paid_amount += amount
            installment.due_amount -= amount

            if installment.due_amount <= 0:
                installment.status = 'paid'
                installment.payment_date = timezone.now()

            installment.save()
            
            # Check if all installments for the purchase are paid
            all_paid = not Installment.objects.filter(purchase=installment.purchase, status='due').exists()

            if all_paid:
                # Mark the purchase as paid
                purchase = installment.purchase
                purchase.status = 'paid'
                purchase.save()

            return Response({"detail": "Payment successful."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NextDueInstallmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Get the next due installment
        next_due_installment = Installment.objects.filter(
            purchase__customer=user, 
            status='due', 
            due_date__gte=timezone.now()
        ).order_by('due_date').first()

        if not next_due_installment:
            return Response({"detail": "No due installments found."}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the next due installment data
        installment_data = {
            "id": next_due_installment.id,
            "installment_number": next_due_installment.installment_number,
            "due_amount": str(next_due_installment.due_amount),
            "due_date": next_due_installment.due_date,
            "status": next_due_installment.status
        }

        return Response(installment_data, status=status.HTTP_200_OK)


class AllInstallmentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Fetch all installments for the authenticated user
        installments = Installment.objects.filter(purchase__customer=user).order_by('due_date')

        # If no installments found, return a message
        if not installments:
            return Response({"detail": "No installments found."}, status=status.HTTP_404_NOT_FOUND)

        # Serialize all installments
        serializer = InstallmentSerializer(installments, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)


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
