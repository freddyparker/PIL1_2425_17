# serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer pour l'inscription des utilisateurs"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'phone', 'first_name', 'last_name', 
            'role', 'password', 'password_confirm'
        )
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return attrs
    
    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        return value
    
    def validate_phone(self, value):
        if CustomUser.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Ce numéro de téléphone est déjà utilisé.")
        return value
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserSerializer(serializers.ModelSerializer):
    """Serializer pour les informations utilisateur"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = CustomUser
        fields = (
            'id', 'username', 'email', 'phone', 'first_name', 'last_name',
            'full_name', 'role', 'profile_picture', 'default_departure',
            'default_destination', 'default_departure_time', 'vehicle_brand',
            'vehicle_model', 'vehicle_color', 'vehicle_plate', 'vehicle_seats',
            'rating', 'total_rides', 'is_verified', 'created_at'
        )
        read_only_fields = ('id', 'rating', 'total_rides', 'is_verified', 'created_at')

class LoginSerializer(serializers.Serializer):
    """Serializer pour la connexion"""
    username = serializers.CharField()  # Peut être email ou téléphone
    password = serializers.CharField()
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            # Essayer de trouver l'utilisateur par email ou téléphone
            user = None
            if '@' in username:
                try:
                    user_obj = CustomUser.objects.get(email=username)
                    user = authenticate(username=user_obj.username, password=password)
                except CustomUser.DoesNotExist:
                    pass
            else:
                try:
                    user_obj = CustomUser.objects.get(phone=username)
                    user = authenticate(username=user_obj.username, password=password)
                except CustomUser.DoesNotExist:
                    pass
            
            if not user:
                raise serializers.ValidationError('Identifiants invalides.')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Email/téléphone et mot de passe requis.')