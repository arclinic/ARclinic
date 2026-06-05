from rest_framework import serializers
from .models import (
    Campaign, Lead, EmailTemplate, MailingCampaign,
    SEOKeyword, ContentPage, ABTest, AnalyticsEvent,
)


class CampaignSerializer(serializers.ModelSerializer):
    roi = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = "__all__"
        read_only_fields = ["spent"]

    def get_roi(self, obj):
        return obj.roi()


class LeadSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]

    def get_full_name(self, obj):
        return obj.full_name


class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = "__all__"


class MailingCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = MailingCampaign
        fields = "__all__"
        read_only_fields = ["sent_at", "opened_count", "clicked_count"]


class SEOKeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SEOKeyword
        fields = "__all__"


class ContentPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentPage
        fields = "__all__"


class ABTestSerializer(serializers.ModelSerializer):
    winner = serializers.SerializerMethodField()

    class Meta:
        model = ABTest
        fields = "__all__"

    def get_winner(self, obj):
        if obj.a_views and obj.b_views:
            a_rate = obj.a_conversions / obj.a_views
            b_rate = obj.b_conversions / obj.b_views
            if a_rate > b_rate:
                return "A"
            if b_rate > a_rate:
                return "B"
        return None


class AnalyticsEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsEvent
        fields = "__all__"
        read_only_fields = ["created_at"]


class MarketingDashboardSerializer(serializers.Serializer):
    total_campaigns = serializers.IntegerField()
    active_campaigns = serializers.IntegerField()
    total_leads = serializers.IntegerField()
    new_leads_today = serializers.IntegerField()
    total_spent = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_budget = serializers.DecimalField(max_digits=12, decimal_places=2)
