from rest_framework import serializers
from .models import Caller

class CallerRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = Caller
        fields = ['full_name', 'phone_number', 'email', 'password']

    def validate_phone_number(self, value):
        # Ensure it follows 09XXXXXXXXX format
        if not value.startswith('09') or len(value) != 11:
            raise serializers.ValidationError("Phone must be in 09XXXXXXXXX format")
        if Caller.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Phone number already registered")
        return value

    def validate_email(self, value):
        if value and Caller.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value

    def create(self, validated_data):
        # Extract raw password
        raw_password = validated_data.pop('password')
        # Create instance without password first
        caller = Caller(**validated_data)
        # Hash password using model helper
        caller.set_password(raw_password)
        caller.save()
        return caller



class CallerLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
