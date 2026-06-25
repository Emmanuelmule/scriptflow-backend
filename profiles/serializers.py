from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Writer


class RegisterSerializer(serializers.ModelSerializer):
    password  = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model  = Writer
        fields = [
            'email', 'full_name', 'phone', 'password', 'password2',
            'bio', 'specialties', 'experience', 'education'
        ]

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        writer   = Writer(**validated_data)
        writer.set_password(password)
        writer.save()
        return writer


class LoginSerializer(serializers.Serializer):
    email    = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(email=data['email'])
            if not user.check_password(data['password']):
                raise serializers.ValidationError("Invalid email or password.")
            if not user.is_active:
                raise serializers.ValidationError("Account is suspended.")
            data['user'] = user
            return data
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")


class WriterProfileSerializer(serializers.ModelSerializer):
    is_membership_active = serializers.ReadOnlyField()

    class Meta:
        model  = Writer
        fields = [
            'id', 'email', 'full_name', 'phone', 'role',
            'bio', 'specialties', 'experience', 'education',
            'rating', 'photo', 'is_membership_active', 'created_at'
        ]
        read_only_fields = ['id', 'email', 'role', 'rating', 'created_at']


class AdminWriterListSerializer(serializers.ModelSerializer):
    is_membership_active = serializers.ReadOnlyField()

    class Meta:
        model  = Writer
        fields = [
            'id', 'full_name', 'email', 'phone', 'rating',
            'is_membership_active', 'is_active', 'created_at'
        ]