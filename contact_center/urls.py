from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TicketViewSet, TicketCommentViewSet,
    ChatSessionViewSet, MessageViewSet, CallSessionViewSet,
)

router = DefaultRouter()
router.register(r"tickets", TicketViewSet)
router.register(r"ticket-comments", TicketCommentViewSet)
router.register(r"chats", ChatSessionViewSet)
router.register(r"messages", MessageViewSet)
router.register(r"calls", CallSessionViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
