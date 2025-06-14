# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """Modèle utilisateur personnalisé pour IFRI Covoiturage"""
    
    ROLE_CHOICES = [
        ('conducteur', 'Conducteur'),
        ('passager', 'Passager'),
        ('both', 'Les deux'),
    ]
    
    # Informations personnelles obligatoires
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True)
    
    # Rôle et préférences
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='passager')
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    # Préférences de trajet
    default_departure = models.CharField(max_length=255, blank=True)
    default_destination = models.CharField(max_length=255, blank=True)
    default_departure_time = models.TimeField(blank=True, null=True)
    
    # Informations véhicule (pour conducteurs)
    vehicle_brand = models.CharField(max_length=100, blank=True)
    vehicle_model = models.CharField(max_length=100, blank=True)
    vehicle_color = models.CharField(max_length=50, blank=True)
    vehicle_plate = models.CharField(max_length=20, blank=True)
    vehicle_seats = models.IntegerField(default=4, blank=True, null=True)
    
    # Statistiques
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)
    total_rides = models.IntegerField(default=0)
    
    # Métadonnées
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"