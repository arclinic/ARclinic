import pytest
from django.db import IntegrityError
from marketing.models import Campaign, Lead, ContentPage


@pytest.mark.django_db
class TestCampaign:
    def test_create_campaign(self):
        campaign = Campaign.objects.create(
            name="Тестовая кампания",
            campaign_type="context",
            budget=10000,
        )
        assert campaign.status == "draft"
        assert str(campaign) == "Тестовая кампания"
        assert campaign.roi() == 0

    def test_campaign_status_change(self):
        campaign = Campaign.objects.create(
            name="SEO кампания", campaign_type="seo"
        )
        campaign.status = "active"
        campaign.save()
        assert Campaign.objects.get(id=campaign.id).status == "active"


@pytest.mark.django_db
class TestLead:
    def test_create_lead(self):
        lead = Lead.objects.create(
            first_name="Иван",
            last_name="Петров",
            phone="+79161234567",
            source="site",
        )
        assert lead.status == "new"
        assert lead.full_name == "Петров Иван"

    def test_lead_required_fields(self):
        from django.core.exceptions import ValidationError
        lead = Lead(first_name="Иван", source="site")
        with pytest.raises(ValidationError):
            lead.full_clean()


@pytest.mark.django_db
class TestContentPage:
    def test_unique_slug(self):
        ContentPage.objects.create(name="Page 1", slug="about")
        with pytest.raises(IntegrityError):
            ContentPage.objects.create(name="Page 2", slug="about")
