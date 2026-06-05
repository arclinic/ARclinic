from celery import shared_task


@shared_task
def check_sla_violations():
    pass


@shared_task
def send_ticket_notification(ticket_id: int):
    pass
