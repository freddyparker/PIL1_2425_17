from django.contrib import admin
from django.utils.html import format_html
from .models import Ride, RideRequest, Review

@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    """Administration des trajets"""
    
    list_display = (
        'id', 'user_display', 'ride_type', 'status',
        'departure_short', 'destination_short', 
        'departure_date', 'departure_time',
        'available_seats', 'price', 'requests_count',
        'created_at'
    )
    
    list_filter = (
        'ride_type', 'status', 'is_recurring', 
        'departure_date', 'created_at'
    )
    
    search_fields = (
        'user__first_name', 'user__last_name', 'user__email',
        'departure_address', 'destination_address'
    )
    
    list_editable = ('status',)
    
    date_hierarchy = 'departure_date'
    
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('user', 'ride_type', 'status')
        }),
        ('Itinéraire', {
            'fields': (
                'departure_address', 'departure_latitude', 'departure_longitude',
                'destination_address', 'destination_latitude', 'destination_longitude'
            )
        }),
        ('Horaires', {
            'fields': ('departure_date', 'departure_time', 'is_recurring', 'recurring_days')
        }),
        ('Détails', {
            'fields': ('available_seats', 'price', 'notes')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_display(self, obj):
        """Afficher le nom de l'utilisateur"""
        return obj.user.get_full_name()
    user_display.short_description = 'Utilisateur'
    user_display.admin_order_field = 'user__first_name'
    
    def departure_short(self, obj):
        """Afficher le départ en version courte"""
        return obj.departure_address[:30] + "..." if len(obj.departure_address) > 30 else obj.departure_address
    departure_short.short_description = 'Départ'
    
    def destination_short(self, obj):
        """Afficher la destination en version courte"""
        return obj.destination_address[:30] + "..." if len(obj.destination_address) > 30 else obj.destination_address
    destination_short.short_description = 'Destination'
    
    def requests_count(self, obj):
        """Afficher le nombre de demandes"""
        count = obj.requests.count()
        if count > 0:
            return format_html(
                '<span style="background-color: #ffc107; padding: 2px 6px; border-radius: 3px;">{}</span>',
                count
            )
        return count
    requests_count.short_description = 'Demandes'

@admin.register(RideRequest)
class RideRequestAdmin(admin.ModelAdmin):
    """Administration des demandes de trajet"""
    
    list_display = (
        'id', 'passenger_display', 'ride_short', 
        'status', 'seats_requested', 'created_at'
    )
    
    list_filter = ('status', 'created_at', 'seats_requested')
    
    search_fields = (
        'passenger__first_name', 'passenger__last_name',
        'ride__departure_address', 'ride__destination_address'
    )
    
    list_editable = ('status',)
    
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Demande', {
            'fields': ('ride', 'passenger', 'status', 'seats_requested')
        }),
        ('Message', {
            'fields': ('message',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def passenger_display(self, obj):
        """Afficher le nom du passager"""
        return obj.passenger.get_full_name()
    passenger_display.short_description = 'Passager'
    passenger_display.admin_order_field = 'passenger__first_name'
    
    def ride_short(self, obj):
        """Afficher le trajet en version courte"""
        return f"{obj.ride.departure_address[:20]}... → {obj.ride.destination_address[:20]}..."
    ride_short.short_description = 'Trajet'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Administration des évaluations"""
    
    list_display = (
        'id', 'reviewer_display', 'reviewed_display',
        'rating', 'ride_short', 'created_at'
    )
    
    list_filter = ('rating', 'created_at')
    
    search_fields = (
        'reviewer__first_name', 'reviewer__last_name',
        'reviewed__first_name', 'reviewed__last_name'
    )
    
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Évaluation', {
            'fields': ('ride', 'reviewer', 'reviewed', 'rating')
        }),
        ('Commentaire', {
            'fields': ('comment',)
        }),
        ('Métadonnées', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def reviewer_display(self, obj):
        """Afficher l'évaluateur"""
        return obj.reviewer.get_full_name()
    reviewer_display.short_description = 'Évaluateur'
    
    def reviewed_display(self, obj):
        """Afficher l'évalué"""
        return obj.reviewed.get_full_name()
    reviewed_display.short_description = 'Évalué'
    
    def ride_short(self, obj):
        """Afficher le trajet"""
        return f"Trajet #{obj.ride.id}"
    ride_short.short_description = 'Trajet'
    
    def get_queryset(self, request):
        """Optimiser les requêtes"""
        return super().get_queryset(request).select_related(
            'reviewer', 'reviewed', 'ride'
        )