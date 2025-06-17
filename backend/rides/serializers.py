# serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Ride, RideRequest, Review

User = get_user_model()

class UserBasicSerializer(serializers.ModelSerializer):
    """Serializer basique pour afficher les informations utilisateur dans les trajets"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'full_name', 'profile_picture', 'rating', 'phone')

class RideSerializer(serializers.ModelSerializer):
    """Serializer pour les trajets"""
    user = UserBasicSerializer(read_only=True)
    user_id = serializers.IntegerField(read_only=True)
    available_requests = serializers.SerializerMethodField()
    
    class Meta:
        model = Ride
        fields = (
            'id', 'user', 'user_id', 'ride_type', 'status',
            'departure_address', 'departure_latitude', 'departure_longitude',
            'destination_address', 'destination_latitude', 'destination_longitude',
            'departure_date', 'departure_time',
            'is_recurring', 'recurring_days',
            'available_seats', 'price', 'notes',
            'available_requests',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'user', 'user_id', 'created_at', 'updated_at')
    
    def get_available_requests(self, obj):
        """Retourne le nombre de demandes en attente"""
        return obj.requests.filter(status='pending').count()
    
    def validate_departure_date(self, value):
        """Valider que la date de départ n'est pas dans le passé"""
        from datetime import date
        if value < date.today():
            raise serializers.ValidationError("La date de départ ne peut pas être dans le passé.")
        return value
    
    def validate_available_seats(self, value):
        """Valider le nombre de places disponibles"""
        if value < 1 or value > 8:
            raise serializers.ValidationError("Le nombre de places doit être entre 1 et 8.")
        return value
    
    def validate(self, attrs):
        """Validations globales"""
        # Pour les offres, vérifier les informations véhicule
        if attrs.get('ride_type') == 'offer':
            user = self.context['request'].user
            if not user.vehicle_brand or not user.vehicle_model:
                raise serializers.ValidationError(
                    "Veuillez compléter les informations de votre véhicule dans votre profil."
                )
        
        # Valider les coordonnées GPS si fournies
        lat_fields = ['departure_latitude', 'destination_latitude']
        lon_fields = ['departure_longitude', 'destination_longitude']
        
        for lat_field in lat_fields:
            lat_value = attrs.get(lat_field)
            if lat_value and (lat_value < -90 or lat_value > 90):
                raise serializers.ValidationError(f"{lat_field} doit être entre -90 et 90.")
        
        for lon_field in lon_fields:
            lon_value = attrs.get(lon_field)
            if lon_value and (lon_value < -180 or lon_value > 180):
                raise serializers.ValidationError(f"{lon_field} doit être entre -180 et 180.")
        
        return attrs

class RideRequestSerializer(serializers.ModelSerializer):
    """Serializer pour les demandes de trajet"""
    passenger = UserBasicSerializer(read_only=True)
    passenger_id = serializers.IntegerField(read_only=True)
    ride = RideSerializer(read_only=True)
    ride_id = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = RideRequest
        fields = (
            'id', 'ride', 'ride_id', 'passenger', 'passenger_id',
            'status', 'seats_requested', 'message',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'passenger', 'passenger_id', 'ride_id', 'created_at', 'updated_at')
    
    def validate_seats_requested(self, value):
        """Valider le nombre de places demandées"""
        if value < 1:
            raise serializers.ValidationError("Le nombre de places doit être au moins 1.")
        return value

class ReviewSerializer(serializers.ModelSerializer):
    """Serializer pour les évaluations"""
    reviewer = UserBasicSerializer(read_only=True)
    reviewed = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = (
            'id', 'ride', 'reviewer', 'reviewed',
            'rating', 'comment', 'created_at'
        )
        read_only_fields = ('id', 'reviewer', 'reviewed', 'created_at')
    
    def validate_rating(self, value):
        """Valider la note"""
        if value < 1 or value > 5:
            raise serializers.ValidationError("La note doit être entre 1 et 5.")
        return value

class RideSearchSerializer(serializers.Serializer):
    """Serializer pour la recherche de trajets"""
    departure_lat = serializers.DecimalField(max_digits=10, decimal_places=8)
    departure_lon = serializers.DecimalField(max_digits=11, decimal_places=8)
    destination_lat = serializers.DecimalField(max_digits=10, decimal_places=8)
    destination_lon = serializers.DecimalField(max_digits=11, decimal_places=8)
    departure_date = serializers.DateField()
    departure_time = serializers.TimeField(required=False)
    max_distance = serializers.IntegerField(default=10, min_value=1, max_value=50)
    max_time_diff = serializers.IntegerField(default=60, min_value=15, max_value=240)
    
    def validate_departure_date(self, value):
        """Valider que la date de recherche n'est pas dans le passé"""
        from datetime import date
        if value < date.today():
            raise serializers.ValidationError("La date de recherche ne peut pas être dans le passé.")
        return value