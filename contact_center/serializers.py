from rest_framework import serializers
from .models import Ticket, TicketComment, ChatSession, Message, CallSession


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = "__all__"


class TicketCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketComment
        fields = "__all__"


class ChatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSession
        fields = "__all__"


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"


class CallSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallSession
        fields = "__all__"
