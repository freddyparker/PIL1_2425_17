# chat/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Conversation, Message

User = get_user_model()

class UserBasicSerializer(serializers.ModelSerializer):
    """Serializer basique pour les utilisateurs dans le chat"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'full_name', 'profile_picture')

class MessageSerializer(serializers.ModelSerializer):
    """Serializer pour les messages"""
    sender = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ('id', 'conversation', 'sender', 'content', 'is_read', 'created_at')
        read_only_fields = ('id', 'sender', 'created_at')

class ConversationSerializer(serializers.ModelSerializer):
    """Serializer pour les conversations"""
    participants = UserBasicSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    other_participant = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = (
            'id', 'participants', 'ride', 'name', 
            'last_message', 'other_participant', 'unread_count',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def get_last_message(self, obj):
        """Récupérer le dernier message"""
        last_message = obj.messages.last()
        if last_message:
            return {
                'content': last_message.content,
                'sender': last_message.sender.get_full_name(),
                'created_at': last_message.created_at
            }
        return None
    
    def get_other_participant(self, obj):
        """Récupérer l'autre participant dans une conversation privée"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            other = obj.get_other_participant(request.user)
            if other:
                return UserBasicSerializer(other).data
        return None
    
    def get_unread_count(self, obj):
        """Compter les messages non lus"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.messages.filter(
                is_read=False
            ).exclude(sender=request.user).count()
        return 0