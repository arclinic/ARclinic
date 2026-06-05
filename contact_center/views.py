from rest_framework import viewsets
from .models import Ticket, TicketComment, ChatSession, Message, CallSession
from .serializers import (
    TicketSerializer, TicketCommentSerializer,
    ChatSessionSerializer, MessageSerializer, CallSessionSerializer,
)


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    filterset_fields = ["status", "priority", "category", "assigned_to"]


class TicketCommentViewSet(viewsets.ModelViewSet):
    queryset = TicketComment.objects.all()
    serializer_class = TicketCommentSerializer


class ChatSessionViewSet(viewsets.ModelViewSet):
    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionSerializer


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class CallSessionViewSet(viewsets.ModelViewSet):
    queryset = CallSession.objects.all()
    serializer_class = CallSessionSerializer
