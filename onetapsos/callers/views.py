from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CallerRegistrationSerializer, CallerLoginSerializer
from .models import Caller


class CallerRegisterView(APIView):
    def post(self, request):
        serializer = CallerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            caller = serializer.save()
            return Response({
                "caller_id": caller.caller_id,
                "full_name": caller.full_name,
                "phone_number": caller.phone_number,
                "email": caller.email,
                "message": "Caller registered successfully"
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CallerLoginView(APIView):
    def post(self, request):
        serializer = CallerLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            try:
                caller = Caller.objects.get(email=email)
            except Caller.DoesNotExist:
                return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

            if caller.check_password(password):
                return Response({
                    "caller_id": caller.caller_id,
                    "full_name": caller.full_name,
                    "phone_number": caller.phone_number,
                    "email": caller.email,
                    "token": "sampletoken123"  # 🔑 replace with JWT later
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
