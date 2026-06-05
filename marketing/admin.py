from django.contrib import admin

from .models import (
    Campaign, Lead, EmailTemplate, MailingCampaign,
    SEOKeyword, ContentPage, ABTest, AnalyticsEvent,
)


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ["name", "campaign_type", "status", "budget", "spent", "start_date"]
    list_filter = ["status", "campaign_type"]
    search_fields = ["name"]


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "phone", "status", "source", "created_at"]
    list_filter = ["status", "source"]
    search_fields = ["first_name", "last_name", "phone", "email"]


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "subject"]


@admin.register(MailingCampaign)
class MailingCampaignAdmin(admin.ModelAdmin):
    list_display = ["name", "status", "scheduled_at", "sent_at", "opened_count"]
    list_filter = ["status"]


@admin.register(SEOKeyword)
class SEOKeywordAdmin(admin.ModelAdmin):
    list_display = ["keyword", "position", "volume"]
    search_fields = ["keyword"]


@admin.register(ContentPage)
class ContentPageAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "is_published"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ABTest)
class ABTestAdmin(admin.ModelAdmin):
    list_display = ["name", "page_url", "starts_at", "ends_at"]


@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    list_display = ["event_type", "page_url", "created_at"]
    list_filter = ["event_type"]
