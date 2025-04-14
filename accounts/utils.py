import random
from django.core.mail import send_mail
from django.utils import timezone
from .models import OTP

def generate_otp():
    return str(random.randint(100000, 999999))  # Generate a random 6-digit OTP

def send_otp_to_user(user):
    otp_code = generate_otp()
    expires_at = timezone.now() + timezone.timedelta(minutes=10)  # OTP expires in 10 minutes

    # Create or update the OTP record for the user
    OTP.objects.update_or_create(
        user=user,
        defaults={'code': otp_code, 'expires_at': expires_at}
    )

    # Send OTP to the user's email
    subject = 'Your OTP Code'
    message = f'Your OTP code is: {otp_code}. It will expire in 10 minutes.'
    send_mail(subject, message, 'youremail@example.com', [user.email])
