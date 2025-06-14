# utils.py
from math import radians, cos, sin, asin, sqrt
from django.db.models import Q
from datetime import datetime, timedelta
from .models import Ride

def haversine(lon1, lat1, lon2, lat2):
    """
    Calcule la distance entre deux points GPS en kilomètres
    """
    # Convertir degrés en radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    
    # Formule haversine
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371  # Rayon de la Terre en km
    
    return c * r

def time_difference_minutes(time1, time2):
    """Calcule la différence en minutes entre deux heures"""
    if not time1 or not time2:
        return 0
    
    minutes1 = time1.hour * 60 + time1.minute
    minutes2 = time2.hour * 60 + time2.minute
    
    return abs(minutes1 - minutes2)

def find_matching_rides(departure_lat, departure_lon, destination_lat, destination_lon, 
                       departure_date, departure_time=None, max_distance=10, max_time_diff=60):
    """
    Trouve les trajets compatibles selon les critères de recherche
    
    Args:
        departure_lat, departure_lon: Coordonnées point de départ
        destination_lat, destination_lon: Coordonnées destination
        departure_date: Date du trajet
        departure_time: Heure souhaitée (optionnel)
        max_distance: Distance maximale en km (défaut: 10km)
        max_time_diff: Différence horaire max en minutes (défaut: 60min)
    
    Returns:
        Liste des trajets compatibles avec scores de compatibilité
    """
    
    # Rechercher les offres actives pour la date donnée
    offers = Ride.objects.filter(
        ride_type='offer',
        status='active',
        departure_date=departure_date,
        available_seats__gt=0
    ).select_related('user')
    
    # Inclure aussi les trajets récurrents
    if departure_date:
        weekday = departure_date.strftime('%A').lower()
        # Mapper les jours français/anglais
        day_mapping = {
            'monday': 'lundi', 'tuesday': 'mardi', 'wednesday': 'mercredi',
            'thursday': 'jeudi', 'friday': 'vendredi', 'saturday': 'samedi', 
            'sunday': 'dimanche'
        }
        french_day = day_mapping.get(weekday, weekday)
        
        recurring_offers = Ride.objects.filter(
            ride_type='offer',
            status='active',
            is_recurring=True,
            recurring_days__contains=weekday,
            available_seats__gt=0
        ).select_related('user')
        
        offers = offers.union(recurring_offers)
    
    matching_rides = []
    
    for offer in offers:
        # Vérifier que les coordonnées GPS existent
        if not all([offer.departure_latitude, offer.departure_longitude, 
                   offer.destination_latitude, offer.destination_longitude]):
            continue
        
        # Calculer distances géographiques
        dep_distance = haversine(
            departure_lon, departure_lat,
            float(offer.departure_longitude), float(offer.departure_latitude)
        )
        
        dest_distance = haversine(
            destination_lon, destination_lat,
            float(offer.destination_longitude), float(offer.destination_latitude)
        )
        
        # Filtrer par distance géographique
        if dep_distance <= max_distance and dest_distance <= max_distance:
            
            # Calculer compatibilité horaire
            time_diff = 0
            if departure_time and offer.departure_time:
                time_diff = time_difference_minutes(departure_time, offer.departure_time)
            
            # Filtrer par compatibilité horaire
            if not departure_time or time_diff <= max_time_diff:
                
                # Calculer score de compatibilité (plus bas = mieux)
                distance_score = (dep_distance + dest_distance) / 2
                time_score = time_diff / 10  # Normaliser le temps
                compatibility_score = distance_score + time_score
                
                matching_rides.append({
                    'ride': offer,
                    'departure_distance': dep_distance,
                    'destination_distance': dest_distance,
                    'time_difference': time_diff,
                    'compatibility_score': compatibility_score
                })
    
    # Trier par score de compatibilité (meilleurs en premier)
    matching_rides.sort(key=lambda x: x['compatibility_score'])
    
    return matching_rides

def calculate_estimated_price(distance_km, base_price_per_km=0.15):
    """
    Calcule un prix estimé basé sur la distance
    
    Args:
        distance_km: Distance en kilomètres
        base_price_per_km: Prix de base par kilomètre
    
    Returns:
        Prix estimé en FCFA
    """
    if distance_km <= 0:
        return 0
    
    # Prix de base + distance
    base_price = 500  # FCFA
    distance_price = distance_km * base_price_per_km * 655  # Conversion en FCFA
    
    total_price = base_price + distance_price
    
    # Arrondir aux 100 FCFA les plus proches
    return round(total_price / 100) * 100