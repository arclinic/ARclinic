from celery import shared_task


@shared_task
def send_appointment_reminder(appointment_id: int):
    pass


@shared_task
def check_low_stock():
    pass
