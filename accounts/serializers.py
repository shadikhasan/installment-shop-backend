from rest_framework import serializers
from .models import Customer
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import authenticate
from django.core.mail import send_mail
import random

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = Customer.objects.create_user(**validated_data)
        otp = str(random.randint(100000, 999999))
        user.otp_code = otp
        user.otp_expiry = timezone.now() + timedelta(minutes=10)
        user.is_verified = False
        user.save()

        # Send OTP via email
        send_mail(
            subject="Your OTP Code",
            message=f"Your OTP code is {otp}",
            from_email=None,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return user

class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField()

    def validate(self, attrs):
        try:
            user = Customer.objects.get(email=attrs['email'])
        except Customer.DoesNotExist:
            raise serializers.ValidationError("User not found.")

        if user.otp_code != attrs['otp_code']:
            raise serializers.ValidationError("Invalid OTP.")

        if timezone.now() > user.otp_expiry:
            raise serializers.ValidationError("OTP expired.")

        user.is_verified = True
        user.otp_code = ''
        user.save()
        return attrs

from django.contrib.auth import get_user_model

User = get_user_model()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials.")

        if not user.check_password(data['password']):
            raise serializers.ValidationError("Invalid credentials.")

        if not user.is_verified:
            raise serializers.ValidationError("Account not verified with OTP.")

        data['user'] = user
        return data
