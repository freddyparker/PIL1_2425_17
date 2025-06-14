# views.py
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import login

from .models import CustomUser
from .serializers import UserRegistrationSerializer, UserSerializer, LoginSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Inscription d'un nouvel utilisateur"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data,
            'message': 'Inscription réussie!'
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Connexion utilisateur"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data,
            'message': 'Connexion réussie!'
        })
    return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Déconnexion utilisateur"""
    try:
        token = Token.objects.get(user=request.user)
        token.delete()
        return Response({'message': 'Déconnexion réussie!'})
    except Token.DoesNotExist:
        return Response({'error': 'Token non trouvé'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """Récupération et modification du profil utilisateur"""
    if request.method == 'GET':
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'user': serializer.data,
                'message': 'Profil mis à jour avec succès!'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    """Demande de réinitialisation de mot de passe"""
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email requis'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = CustomUser.objects.get(email=email)
        
        # Générer token de réinitialisation
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Créer lien de réinitialisation
        reset_link = f"http://localhost:3000/reset-password/{uid}/{token}/"
        
        # Envoyer email (en développement, apparaîtra dans la console)
        send_mail(
            subject='Réinitialisation de mot de passe - IFRI Covoiturage',
            message=f'''
Bonjour {user.get_full_name()},

Vous avez demandé une réinitialisation de votre mot de passe.
Cliquez sur le lien suivant pour réinitialiser votre mot de passe :

{reset_link}

Ce lien expirera dans 24 heures.

Si vous n'avez pas demandé cette réinitialisation, ignorez ce message.

L'équipe IFRI Covoiturage
            ''',
            from_email='noreply@ifri-covoiturage.com',
            recipient_list=[email],
        )
        
        return Response({
            'message': 'Email de réinitialisation envoyé avec succès!'
        })
        
    except CustomUser.DoesNotExist:
        return Response({
            'error': 'Aucun utilisateur trouvé avec cette adresse email'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request, uid, token):
    """Réinitialisation du mot de passe"""
    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = CustomUser.objects.get(pk=user_id)
        
        if default_token_generator.check_token(user, token):
            new_password = request.data.get('password')
            if not new_password:
                return Response({'error': 'Nouveau mot de passe requis'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(new_password)
            user.save()
            
            return Response({'message': 'Mot de passe réinitialisé avec succès!'})
        else:
            return Response({'error': 'Token invalide ou expiré'}, 
                          status=status.HTTP_400_BAD_REQUEST)
            
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        return Response({'error': 'Lien invalide'}, status=status.HTTP_400_BAD_REQUEST)