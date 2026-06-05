from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CampaignViewSet, LeadViewSet, EmailTemplateViewSet,
    MailingCampaignViewSet, SEOKeywordViewSet,
    ContentPageViewSet, ABTestViewSet,
    AnalyticsEventViewSet, DashboardViewSet,
)

router = DefaultRouter()
router.register(r"campaigns", CampaignViewSet)
router.register(r"leads", LeadViewSet)
router.register(r"email-templates", EmailTemplateViewSet)
router.register(r"mailing-campaigns", MailingCampaignViewSet)
router.register(r"seo-keywords", SEOKeywordViewSet)
router.register(r"content-pages", ContentPageViewSet)
router.register(r"ab-tests", ABTestViewSet)
router.register(r"analytics-events", AnalyticsEventViewSet)
router.register(r"dashboard", DashboardViewSet, basename="dashboard")

urlpatterns = [
    path("", include(router.urls)),
]
