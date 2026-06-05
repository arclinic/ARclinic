from django.contrib import admin
from .models import Ticket, ChatSession, CallSession, KnowledgeBaseArticle


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ["subject", "status", "priority", "category", "assigned_to", "created_at"]
    list_filter = ["status", "priority", "category"]


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ["client_name", "source", "status", "operator_id", "created_at"]
    list_filter = ["source", "status"]


@admin.register(CallSession)
class CallSessionAdmin(admin.ModelAdmin):
    list_display = ["caller_phone", "status", "duration", "started_at"]
    list_filter = ["status"]


@admin.register(KnowledgeBaseArticle)
class KnowledgeBaseArticleAdmin(admin.ModelAdmin):
    list_display = ["name", "category"]
    list_filter = ["category"]
