from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.db.models import Sum
from datetime import timedelta
from myapp.models import Installment, Purchase

class WeeklyReportView(APIView):
    #permission_classes = [IsAdminUser]

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
        #permission_classes = [IsAdminUser]

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