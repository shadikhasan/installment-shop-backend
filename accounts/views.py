class VerifyOtpView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        try:
            user = Customer.objects.get(email=email, otp_code=otp)
            if timezone.now() > user.otp_expiry:
                return Response({'error': 'OTP expired'}, status=400)
            user.is_verified = True
            user.is_active = True
            user.otp_code = ''
            user.save()
            return Response({'message': 'Account verified'})
        except Customer.DoesNotExist:
            return Response({'error': 'Invalid OTP'}, status=400)
