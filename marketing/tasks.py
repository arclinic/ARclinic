import logging

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from .models import MailingCampaign, Lead

logger = logging.getLogger(__name__)


@shared_task
def send_email_campaign(mailing_id: int):
    try:
        mailing = MailingCampaign.objects.get(id=mailing_id)
        recipients = [e.strip() for e in mailing.recipient_list.split(",") if e.strip()]
        subject = mailing.template.subject
        body = mailing.template.body

        for email in recipients:
            try:
                send_mail(
                    subject,
                    body,
                    settings.DEFAULT_FROM_EMAIL or "noreply@arclinic.ru",
                    [email],
                    fail_silently=False,
                )
            except Exception as e:
                logger.error(f"Failed to send to {email}: {e}")

        mailing.status = "sent"
        mailing.sent_at = timezone.now()
        mailing.save()
        return f"Sent to {len(recipients)} recipients"
    except MailingCampaign.DoesNotExist:
        logger.error(f"MailingCampaign {mailing_id} not found")
        return None


@shared_task
def import_leads_from_source(source: str):
    leads = Lead.objects.filter(source=source, status="new").count()
    return f"Found {leads} leads from {source}"


@shared_task
def calculate_campaign_roi(campaign_id: int):
    from .models import Campaign

    try:
        campaign = Campaign.objects.get(id=campaign_id)
        if campaign.budget and campaign.spent:
            roi = (campaign.spent / campaign.budget) * 100
            logger.info(f"Campaign {campaign.name} ROI: {roi:.1f}%")
        return None
    except Campaign.DoesNotExist:
        return None
