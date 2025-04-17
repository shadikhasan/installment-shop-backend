from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from .models import Purchase, Installment, Product
from rest_framework.exceptions import PermissionDenied
from .serializers import *
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated, AllowAny
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
from django.contrib.auth import get_user_model     

from django.http import JsonResponse
from rest_framework.decorators import api_view


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
        installment = Installment.objects.filter(
            id=installment_id,
            purchase__customer=user,
            status='due'
        ).first()

        if not installment:
            return Response({"detail": "Installment not found or already paid."}, status=status.HTTP_404_NOT_FOUND)

        is_late = timezone.now() > installment.due_date
        original_due = installment.due_amount

        # Calculate 10% late fee if overdue
        if is_late:
            penalty = (original_due * Decimal('0.10')).quantize(Decimal('0.01'))
            total_due = original_due + penalty
        else:
            penalty = Decimal('0.00')
            total_due = original_due

        serializer = PayInstallmentSerializer(data=request.data, context={'installment': installment})

        if serializer.is_valid():
            amount = serializer.validated_data['amount']

            # Rule: Must pay full amount + penalty if late
            if is_late and amount < total_due:
                return Response(
                    {"detail": f"Late payment! You must pay the full amount including penalty: ৳{total_due}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Rule: Do not allow overpayment
            if amount > total_due:
                return Response(
                    {"detail": f"You cannot pay more than the required amount: ৳{total_due}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Update installment
            installment.paid_amount += amount
            installment.due_amount -= amount
            if is_late:
                installment.late_fee = penalty

            if installment.due_amount <= 0:
                installment.status = 'paid'
                installment.payment_date = timezone.now()

            installment.save()

            # If all installments for this purchase are paid, mark purchase as paid
            if not installment.purchase.installments.filter(status='due').exists():
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
            'product_name': next_due_installment.purchase.product.name,
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


class UserDashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        total_due = Installment.objects.filter(purchase__customer=user).aggregate(
            total_due=Sum('due_amount')
        )['total_due'] or 0

        total_paid = Installment.objects.filter(purchase__customer=user).aggregate(
            total_paid=Sum('paid_amount')
        )['total_paid'] or 0

        total_purchase = Purchase.objects.filter(customer=user).count()

        installment_left = Installment.objects.filter(purchase__customer=user, status='due').count()
        installment_paid = Installment.objects.filter(purchase__customer=user, status='paid').count()

        return Response({
            "total_due": total_due,
            "total_paid": total_paid,
            "total_purchase": total_purchase,
            "installment_left": installment_left,
            "installment_paid": installment_paid
        })

class GlobalDashboardSummaryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        total_products = Product.objects.count()

        return Response({
            "total_products": total_products
        })



User = get_user_model()
class UserStatsAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        total_users = User.objects.count()
        verified_users = User.objects.filter(is_verified=True).count()
        not_verified_users = total_users - verified_users

        return Response({
            "total_users": total_users,
            "verified_users": verified_users,
            "not_verified_users": not_verified_users,
        })