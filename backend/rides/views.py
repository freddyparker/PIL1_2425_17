# views.py
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from datetime import datetime, date

from .models import Ride, RideRequest
from .serializers import RideSerializer, RideRequestSerializer
from .utils import find_matching_rides

class RideListCreateView(generics.ListCreateAPIView):
    """Liste et création des trajets"""
    serializer_class = RideSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['ride_type', 'status', 'departure_date']
    
    def get_queryset(self):
        queryset = Ride.objects.all()
        
        # Filtres personnalisés
        departure = self.request.query_params.get('departure', None)
        destination = self.request.query_params.get('destination', None)
        date_from = self.request.query_params.get('date_from', None)
        
        if departure:
            queryset = queryset.filter(departure_address__icontains=departure)
        if destination:
            queryset = queryset.filter(destination_address__icontains=destination)
        if date_from:
            queryset = queryset.filter(departure_date__gte=date_from)
            
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class RideDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Détail, modification et suppression d'un trajet"""
    serializer_class = RideSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Ride.objects.filter(user=self.request.user)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_rides(request):
    """Recherche de trajets compatibles"""
    departure_lat = request.data.get('departure_lat')
    departure_lon = request.data.get('departure_lon')
    destination_lat = request.data.get('destination_lat')
    destination_lon = request.data.get('destination_lon')
    departure_date = request.data.get('departure_date')
    departure_time = request.data.get('departure_time')
    
    if not all([departure_lat, departure_lon, destination_lat, destination_lon, departure_date]):
        return Response({
            'error': 'Tous les paramètres de recherche sont requis'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Convertir la date et l'heure
        search_date = datetime.strptime(departure_date, '%Y-%m-%d').date()
        search_time = datetime.strptime(departure_time, '%H:%M').time() if departure_time else None
        
        # Utiliser l'algorithme de matching
        matching_rides = find_matching_rides(
            float(departure_lat), float(departure_lon),
            float(destination_lat), float(destination_lon),
            search_date, search_time
        )
        
        # Sérialiser les résultats
        results = []
        for match in matching_rides:
            ride_data = RideSerializer(match['ride']).data
            ride_data['departure_distance'] = round(match['departure_distance'], 2)
            ride_data['destination_distance'] = round(match['destination_distance'], 2)
            ride_data['compatibility_score'] = round(match.get('compatibility_score', 0), 2)
            results.append(ride_data)
        
        return Response({
            'results': results,
            'count': len(results)
        })
        
    except ValueError as e:
        return Response({
            'error': 'Format de date/heure invalide'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_ride(request, ride_id):
    """Demander à participer à un trajet"""
    try:
        ride = Ride.objects.get(id=ride_id, ride_type='offer', status='active')
        
        # Vérifier que ce n'est pas son propre trajet
        if ride.user == request.user:
            return Response({
                'error': 'Vous ne pouvez pas demander à participer à votre propre trajet'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier qu'il n'y a pas déjà une demande
        existing_request = RideRequest.objects.filter(
            ride=ride, passenger=request.user
        ).first()
        
        if existing_request:
            return Response({
                'error': 'Vous avez déjà fait une demande pour ce trajet'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Créer la demande
        ride_request = RideRequest.objects.create(
            ride=ride,
            passenger=request.user,
            seats_requested=request.data.get('seats_requested', 1),
            message=request.data.get('message', '')
        )
        
        serializer = RideRequestSerializer(ride_request)
        return Response({
            'ride_request': serializer.data,
            'message': 'Demande envoyée avec succès!'
        }, status=status.HTTP_201_CREATED)
        
    except Ride.DoesNotExist:
        return Response({
            'error': 'Trajet non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def respond_to_request(request, request_id):
    """Accepter ou refuser une demande de trajet"""
    try:
        ride_request = RideRequest.objects.get(
            id=request_id, ride__user=request.user
        )
        
        action = request.data.get('action')  # 'accept' ou 'decline'
        
        if action == 'accept':
            # Vérifier qu'il y a assez de places
            if ride_request.ride.available_seats >= ride_request.seats_requested:
                ride_request.status = 'accepted'
                ride_request.ride.available_seats -= ride_request.seats_requested
                ride_request.ride.save()
                message = 'Demande acceptée!'
            else:
                return Response({
                    'error': 'Plus assez de places disponibles'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        elif action == 'decline':
            ride_request.status = 'declined'
            message = 'Demande refusée'
        else:
            return Response({
                'error': 'Action invalide (accept ou decline)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        ride_request.save()
        
        serializer = RideRequestSerializer(ride_request)
        return Response({
            'ride_request': serializer.data,
            'message': message
        })
        
    except RideRequest.DoesNotExist:
        return Response({
            'error': 'Demande non trouvée'
        }, status=status.HTTP_404_NOT_FOUND)

class MyRidesView(generics.ListAPIView):
    """Mes trajets (offres et demandes)"""
    serializer_class = RideSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Ride.objects.filter(user=self.request.user).order_by('-created_at')

class RideRequestsView(generics.ListAPIView):
    """Demandes reçues pour mes trajets"""
    serializer_class = RideRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return RideRequest.objects.filter(
            ride__user=self.request.user
        ).order_by('-created_at')