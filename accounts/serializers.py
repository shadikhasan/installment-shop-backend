class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['email', 'password']

    def create(self, validated_data):
        otp = get_random_string(6, allowed_chars='1234567890')
        expiry = timezone.now() + timedelta(minutes=10)
        user = Customer.objects.create(
            email=validated_data['email'],
            otp_code=otp,
            otp_expiry=expiry,
            is_active=False
        )
        user.set_password(validated_data['password'])
        user.save()
        send_otp_email(user.email, otp)
        return user
