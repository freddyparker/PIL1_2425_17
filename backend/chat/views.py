# views.py
# chat/views.py
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

class ConversationListView(generics.ListCreateAPIView):
    """Liste des conversations de l'utilisateur"""
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related('participants', 'messages').distinct()
    
    def perform_create(self, serializer):
        """Créer une nouvelle conversation"""
        conversation = serializer.save()
        conversation.participants.add(self.request.user)

class ConversationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Détail d'une conversation"""
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related('participants')

class MessageListView(generics.ListCreateAPIView):
    """Messages d'une conversation"""
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        conversation_id = self.kwargs['conversation_id']
        conversation = get_object_or_404(
            Conversation, 
            id=conversation_id,
            participants=self.request.user
        )
        return Message.objects.filter(
            conversation=conversation
        ).select_related('sender').order_by('created_at')
    
    def perform_create(self, serializer):
        """Créer un nouveau message"""
        conversation_id = self.kwargs['conversation_id']
        conversation = get_object_or_404(
            Conversation,
            id=conversation_id,
            participants=self.request.user
        )
        serializer.save(
            conversation=conversation,
            sender=self.request.user
        )
        # Mettre à jour la date de dernière activité
        conversation.save()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_conversation(request):
    """Créer une conversation avec un autre utilisateur"""
    other_user_id = request.data.get('user_id')
    ride_id = request.data.get('ride_id', None)
    
    if not other_user_id:
        return Response({
            'error': 'ID utilisateur requis'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        other_user = User.objects.get(id=other_user_id)
        
        # Vérifier qu'une conversation n'existe pas déjà
        existing_conversation = Conversation.objects.filter(
            participants=request.user
        ).filter(
            participants=other_user
        ).first()
        
        if existing_conversation:
            serializer = ConversationSerializer(
                existing_conversation, 
                context={'request': request}
            )
            return Response({
                'conversation': serializer.data,
                'created': False
            })
        
        # Créer nouvelle conversation
        conversation = Conversation.objects.create(
            ride_id=ride_id if ride_id else None
        )
        conversation.participants.add(request.user, other_user)
        
        serializer = ConversationSerializer(
            conversation, 
            context={'request': request}
        )
        return Response({
            'conversation': serializer.data,
            'created': True
        }, status=status.HTTP_201_CREATED)
        
    except User.DoesNotExist:
        return Response({
            'error': 'Utilisateur non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_messages_read(request, conversation_id):
    """Marquer les messages comme lus"""
    try:
        conversation = Conversation.objects.get(
            id=conversation_id,
            participants=request.user
        )
        
        # Marquer tous les messages de la conversation comme lus
        # (sauf ceux envoyés par l'utilisateur actuel)
        updated = Message.objects.filter(
            conversation=conversation,
            is_read=False
        ).exclude(sender=request.user).update(is_read=True)
        
        return Response({
            'message': f'{updated} message(s) marqué(s) comme lu(s)'
        })
        
    except Conversation.DoesNotExist:
        return Response({
            'error': 'Conversation non trouvée'
        }, status=status.HTTP_404_NOT_FOUND)