# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Administration personnalisée pour les utilisateurs"""
    
    # Champs affichés dans la liste
    list_display = (
        'username', 'email', 'phone', 'full_name_display', 
        'role', 'rating', 'total_rides', 'is_verified', 
        'is_active', 'date_joined'
    )
    
    # Champs filtrables
    list_filter = (
        'role', 'is_verified', 'is_active', 'is_staff', 
        'date_joined', 'last_login'
    )
    
    # Champs recherchables
    search_fields = ('username', 'email', 'phone', 'first_name', 'last_name')
    
    # Champs modifiables en liste
    list_editable = ('is_verified', 'is_active')
    
    # Pagination
    list_per_page = 20
    
    # Organisation des champs dans le formulaire
    fieldsets = UserAdmin.fieldsets + (
        ('Informations personnelles IFRI', {
            'fields': ('phone', 'role', 'profile_picture')
        }),
        ('Préférences de trajet', {
            'fields': (
                'default_departure', 'default_destination', 
                'default_departure_time'
            ),
            'classes': ('collapse',)
        }),
        ('Informations véhicule', {
            'fields': (
                'vehicle_brand', 'vehicle_model', 'vehicle_color',
                'vehicle_plate', 'vehicle_seats'
            ),
            'classes': ('collapse',)
        }),
        ('Statistiques', {
            'fields': ('rating', 'total_rides', 'is_verified'),
            'classes': ('collapse',)
        }),
    )
    
    # Champs en lecture seule
    readonly_fields = ('date_joined', 'last_login', 'total_rides')
    
    def full_name_display(self, obj):
        """Afficher le nom complet"""
        return obj.get_full_name()
    full_name_display.short_description = 'Nom complet'
    
    def profile_picture_display(self, obj):
        """Afficher la photo de profil"""
        if obj.profile_picture:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%;" />',
                obj.profile_picture.url
            )
        return "Aucune photo"
    profile_picture_display.short_description = 'Photo'
    
    # Actions personnalisées
    actions = ['verify_users', 'unverify_users']
    
    def verify_users(self, request, queryset):
        """Vérifier les utilisateurs sélectionnés"""
        updated = queryset.update(is_verified=True)
        self.message_user(
            request, 
            f'{updated} utilisateur(s) vérifié(s) avec succès.'
        )
    verify_users.short_description = "Vérifier les utilisateurs sélectionnés"
    
    def unverify_users(self, request, queryset):
        """Dé-vérifier les utilisateurs sélectionnés"""
        updated = queryset.update(is_verified=False)
        self.message_user(
            request, 
            f'{updated} utilisateur(s) dé-vérifié(s) avec succès.'
        )
    unverify_users.short_description = "Dé-vérifier les utilisateurs sélectionnés"