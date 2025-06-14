# urls.py
from django.urls import path
from . import views
from . import consumers  # Ajoutez cette ligne

# ...existing code...

websocket_urlpatterns = [
    path('ws/chat/<int:conversation_id>/', consumers.ChatConsumer.as_asgi()),
]

urlpatterns = [
    path('conversations/', views.ConversationListView.as_view(), name='conversations'),
    path('conversations/<int:pk>/', views.ConversationDetailView.as_view(), name='conversation_detail'),
    path('conversations/<int:conversation_id>/messages/', views.MessageListView.as_view(), name='messages'),
]