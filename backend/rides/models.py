# models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class Ride(models.Model):
    """Modèle pour les trajets (offres et demandes)"""
    
    RIDE_TYPE_CHOICES = [
        ('offer', 'Offre de trajet'),
        ('request', 'Demande de trajet'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé'),
    ]
    
    RECURRING_DAYS = [
        ('monday', 'Lundi'),
        ('tuesday', 'Mardi'),
        ('wednesday', 'Mercredi'),
        ('thursday', 'Jeudi'),
        ('friday', 'Vendredi'),
        ('saturday', 'Samedi'),
        ('sunday', 'Dimanche'),
    ]
    
    # Informations de base
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rides')
    ride_type = models.CharField(max_length=10, choices=RIDE_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Itinéraire
    departure_address = models.CharField(max_length=255)
    departure_latitude = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    departure_longitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    
    destination_address = models.CharField(max_length=255)
    destination_latitude = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    destination_longitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    
    # Horaires
    departure_date = models.DateField()
    departure_time = models.TimeField()
    
    # Récurrence
    is_recurring = models.BooleanField(default=False)
    recurring_days = models.JSONField(blank=True, null=True, help_text="Liste des jours: ['monday', 'tuesday', ...]")
    
    # Details du trajet
    available_seats = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(8)])
    price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    notes = models.TextField(blank=True, help_text="Informations supplémentaires")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.departure_address} → {self.destination_address} ({self.departure_date})"

class RideRequest(models.Model):
    """Modèle pour les demandes de participation à un trajet"""
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('accepted', 'Acceptée'),
        ('declined', 'Refusée'),
        ('cancelled', 'Annulée'),
    ]
    
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, related_name='requests')
    passenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ride_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    seats_requested = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    message = models.TextField(blank=True, help_text="Message au conducteur")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('ride', 'passenger')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.passenger.get_full_name()} → {self.ride}"

class Review(models.Model):
    """Modèle pour les évaluations après trajet"""
    
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    reviewed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('ride', 'reviewer', 'reviewed')
    
    def __str__(self):
        return f"Évaluation de {self.reviewer.get_full_name()} pour {self.reviewed.get_full_name()}"