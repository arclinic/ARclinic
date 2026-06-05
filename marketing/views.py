from datetime import date

from django.db import models
from django.db.models import Sum
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    Campaign, Lead, EmailTemplate, MailingCampaign,
    SEOKeyword, ContentPage, ABTest, AnalyticsEvent,
)
from .serializers import (
    CampaignSerializer, LeadSerializer, EmailTemplateSerializer,
    MailingCampaignSerializer, SEOKeywordSerializer,
    ContentPageSerializer, ABTestSerializer,
    AnalyticsEventSerializer, MarketingDashboardSerializer,
)


class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    filterset_fields = ["status", "campaign_type"]
    search_fields = ["name"]
    ordering_fields = ["budget", "spent", "start_date"]

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        campaign = self.get_object()
        campaign.status = "active"
        campaign.save()
        return Response({"status": "activated"})

    @action(detail=True, methods=["post"])
    def pause(self, request, pk=None):
        campaign = self.get_object()
        campaign.status = "paused"
        campaign.save()
        return Response({"status": "paused"})

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        campaign = self.get_object()
        campaign.status = "completed"
        campaign.save()
        return Response({"status": "completed"})


class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    filterset_fields = ["status", "source", "campaign"]
    search_fields = ["first_name", "last_name", "phone", "email"]
    ordering_fields = ["created_at", "status"]

    @action(detail=False, methods=["get"])
    def stats(self, request):
        total = Lead.objects.count()
        today = Lead.objects.filter(created_at__date=date.today()).count()
        by_source = (
            Lead.objects.values("source")
            .annotate(count=models.Count("id"))
            .order_by("-count")
        )
        by_status = (
            Lead.objects.values("status")
            .annotate(count=models.Count("id"))
            .order_by("-count")
        )
        return Response({
            "total": total,
            "today": today,
            "by_source": by_source,
            "by_status": by_status,
        })

    @action(detail=False, methods=["post"])
    def bulk_status(self, request):
        ids = request.data.get("ids", [])
        new_status = request.data.get("status")
        if not ids or not new_status:
            return Response(
                {"error": "ids and status required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        updated = Lead.objects.filter(id__in=ids).update(status=new_status)
        return Response({"updated": updated})


class EmailTemplateViewSet(viewsets.ModelViewSet):
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    search_fields = ["name", "subject"]


class MailingCampaignViewSet(viewsets.ModelViewSet):
    queryset = MailingCampaign.objects.all()
    serializer_class = MailingCampaignSerializer
    filterset_fields = ["status", "template"]
    ordering_fields = ["scheduled_at", "sent_at"]

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        mailing = self.get_object()
        mailing.status = "sending"
        mailing.save()
        from .tasks import send_email_campaign
        send_email_campaign.delay(mailing.id)
        return Response({"status": "sending_started"})


class SEOKeywordViewSet(viewsets.ModelViewSet):
    queryset = SEOKeyword.objects.all()
    serializer_class = SEOKeywordSerializer
    search_fields = ["keyword"]
    ordering_fields = ["position", "volume"]


class ContentPageViewSet(viewsets.ModelViewSet):
    queryset = ContentPage.objects.all()
    serializer_class = ContentPageSerializer
    search_fields = ["name", "meta_title"]
    filterset_fields = ["is_published"]


class ABTestViewSet(viewsets.ModelViewSet):
    queryset = ABTest.objects.all()
    serializer_class = ABTestSerializer
    filterset_fields = ["page_url"]


class AnalyticsEventViewSet(viewsets.ModelViewSet):
    queryset = AnalyticsEvent.objects.all()
    serializer_class = AnalyticsEventSerializer
    filterset_fields = ["event_type"]
    ordering_fields = ["created_at"]

    @action(detail=False, methods=["post"])
    def track(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DashboardViewSet(viewsets.ViewSet):
    def list(self, request):
        data = {
            "total_campaigns": Campaign.objects.count(),
            "active_campaigns": Campaign.objects.filter(status="active").count(),
            "total_leads": Lead.objects.count(),
            "new_leads_today": Lead.objects.filter(
                created_at__date=date.today()
            ).count(),
            "total_spent": Campaign.objects.aggregate(s=Sum("spent"))["s"] or 0,
            "total_budget": Campaign.objects.aggregate(b=Sum("budget"))["b"] or 0,
        }
        serializer = MarketingDashboardSerializer(data)
        return Response(serializer.data)
