from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.db.models import Sum
from datetime import timedelta
from myapp.models import Installment, Purchase
from collections import defaultdict 
from django.utils.timezone import now

from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import get_user_model
from .serializers import UserPaymentSummarySerializer

class MonthlySummaryChartView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        labels = []
        datasets = defaultdict(list)

        today = now().date()

        for i in range(5, -1, -1):
            month = (today.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
            label = month.strftime("%B")
            labels.append(label)

            # ✅ Correct field name: purchase_date
            purchases = Purchase.objects.filter(
                purchase_date__year=month.year,
                purchase_date__month=month.month
            )

            # ✅ Correct field name: due_date
            installments = Installment.objects.filter(
                due_date__year=month.year,
                due_date__month=month.month
            )

            datasets['total_purchases'].append(purchases.aggregate(Sum('total_price'))['total_price__sum'] or 0)
            datasets['total_paid'].append(installments.aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0)
            datasets['total_due'].append(installments.aggregate(Sum('due_amount'))['due_amount__sum'] or 0)

        return Response({

            'labels': labels,
            'datasets': datasets
        })


User = get_user_model()

class UserPaymentSummaryWeeklyListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserPaymentSummarySerializer
    permission_classes = [IsAdminUser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['range'] = 'weekly'  # We pass 'weekly' to filter purchases/installments
        return context


class UserPaymentSummaryMonthlyListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserPaymentSummarySerializer
    permission_classes = [IsAdminUser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['range'] = 'monthly'  # We pass 'monthly' to filter purchases/installments
        return context

    
