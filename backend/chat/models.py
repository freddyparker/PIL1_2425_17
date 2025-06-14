# models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Conversation(models.Model):
    """Modèle pour les conversations entre utilisateurs"""
    
    participants = models.ManyToManyField(User, related_name='conversations')
    ride = models.ForeignKey('rides.Ride', on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        if self.name:
            return self.name
        return f"Conversation {self.id}"
    
    def get_other_participant(self, user):
        """Retourne l'autre participant dans une conversation à 2"""
        return self.participants.exclude(id=user.id).first()

class Message(models.Model):
    """Modèle pour les messages"""
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.get_full_name()}: {self.content[:50]}..."