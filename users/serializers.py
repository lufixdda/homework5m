from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import ConfirmationCode


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'password']

    def validate_username(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Username cannot be empty.')
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username already exists.')
        return value.strip()

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            is_active=False
        )
        ConfirmationCode.objects.create(
            user=user,
            code=ConfirmationCode.generate_code()
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if user is None:
            raise serializers.ValidationError('Invalid credentials.')
        if not user.is_active:
            raise serializers.ValidationError('User is not confirmed.')
        data['user'] = user
        return data


class ConfirmSerializer(serializers.Serializer):
    username = serializers.CharField()
    code = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            user = User.objects.get(username=data['username'])
        except User.DoesNotExist:
            raise serializers.ValidationError('User not found.')
        try:
            confirmation = user.confirmation_code
        except ConfirmationCode.DoesNotExist:
            raise serializers.ValidationError('No confirmation code found.')
        if confirmation.code != data['code']:
            raise serializers.ValidationError('Invalid confirmation code.')
        data['user'] = user
        return data