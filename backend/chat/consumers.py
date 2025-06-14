# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Conversation, Message

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    """Consumer WebSocket pour la messagerie en temps réel"""
    
    async def connect(self):
        """Connexion WebSocket"""
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.conversation_group_name = f'chat_{self.conversation_id}'
        self.user = self.scope['user']
        
        # Vérifier que l'utilisateur participe à la conversation
        if await self.user_in_conversation():
            # Rejoindre le groupe de conversation
            await self.channel_layer.group_add(
                self.conversation_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        """Déconnexion WebSocket"""
        await self.channel_layer.group_discard(
            self.conversation_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Réception d'un message"""
        text_data_json = json.loads(text_data)
        message_content = text_data_json['message']
        
        # Sauvegarder le message en base
        message = await self.save_message(message_content)
        
        # Envoyer le message au groupe
        await self.channel_layer.group_send(
            self.conversation_group_name,
            {
                'type': 'chat_message',
                'message': {
                    'id': message.id,
                    'content': message.content,
                    'sender': {
                        'id': message.sender.id,
                        'full_name': message.sender.get_full_name(),
                    },
                    'created_at': message.created_at.isoformat(),
                }
            }
        )
    
    async def chat_message(self, event):
        """Envoyer message au WebSocket"""
        message = event['message']
        
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': message
        }))
    
    @database_sync_to_async
    def user_in_conversation(self):
        """Vérifier que l'utilisateur participe à la conversation"""
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            return conversation.participants.filter(id=self.user.id).exists()
        except Conversation.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, content):
        """Sauvegarder le message en base"""
        conversation = Conversation.objects.get(id=self.conversation_id)
        message = Message.objects.create(
            conversation=conversation,
            sender=self.user,
            content=content
        )
        # Mettre à jour la date de dernière activité de la conversation
        conversation.save()
        return message