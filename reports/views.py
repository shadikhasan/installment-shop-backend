from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.db.models import Sum
from datetime import timedelta
from myapp.models import Installment, Purchase
from collections import defaultdict 
from django.utils.timezone import now

class WeeklyReportView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        start = timezone.now() - timedelta(days=7)
        
        # Get distinct customers from Installments within the last 7 days
        installments = Installment.objects.filter(payment_date__gte=start)
        
        # Prepare report data
        report_data = []
        
        for installment in installments:
            # Access related purchase and customer
            purchase = installment.purchase
            customer = purchase.customer
            
            # Aggregate Installment data
            installment_data = Installment.objects.filter(purchase=purchase, payment_date__gte=start).aggregate(
                total_paid=Sum('paid_amount'),
                total_due=Sum('due_amount')
            )
            
            # Aggregate Purchase data
            purchase_data = Purchase.objects.filter(customer=customer, purchase_date__gte=start).aggregate(
                total_purchases=Sum('total_price'),
                total_items=Sum('quantity')
            )
            
            # Combine the data into a dictionary
            customer_report = {
                'customer_id': customer.id,
                'customer_username': customer.username,
                'customer_name': customer.first_name + ' ' + customer.last_name,
                'customer_email': customer.email,
                'purchase_data': purchase_data,
                'installment_data': installment_data,
                'purchase_id': purchase.id,
                'installment_number': installment.installment_number,
                'paid_amount': installment.paid_amount,
                'due_amount': installment.due_amount,
                'status': installment.status,
            }
            
            report_data.append(customer_report)
        
        return Response(report_data)


class MonthlyReportView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        start = timezone.now() - timedelta(days=30)
        
        # Get distinct customers from Installments within the last 7 days
        installments = Installment.objects.filter(payment_date__gte=start)
        
        # Prepare report data
        report_data = []
        
        for installment in installments:
            # Access related purchase and customer
            purchase = installment.purchase
            customer = purchase.customer
            
            # Aggregate Installment data
            installment_data = Installment.objects.filter(purchase=purchase, payment_date__gte=start).aggregate(
                total_paid=Sum('paid_amount'),
                total_due=Sum('due_amount')
            )
            
            # Aggregate Purchase data
            purchase_data = Purchase.objects.filter(customer=customer, purchase_date__gte=start).aggregate(
                total_purchases=Sum('total_price'),
                total_items=Sum('quantity')
            )
            
            # Combine the data into a dictionary
            customer_report = {
                'customer_id': customer.id,
                'customer_username': customer.username,
                'customer_name': customer.first_name + ' ' + customer.last_name,
                'customer_email': customer.email,
                'purchase_data': purchase_data,
                'installment_data': installment_data,
                'purchase_id': purchase.id,
                'installment_number': installment.installment_number,
                'paid_amount': installment.paid_amount,
                'due_amount': installment.due_amount,
                'status': installment.status,
            }
            
            report_data.append(customer_report)
        
        return Response(report_data)
    
    

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
