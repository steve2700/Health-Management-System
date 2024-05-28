# authentication/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Patient, Doctor

@receiver(post_save, sender=Patient)
def send_patient_registration_email(sender, instance, created, **kwargs):
    if created:
        send_mail(
            'Welcome to Our Health Service',
            f'Hello {instance.user.full_name},\n\nThank you for registering as a patient. We are here to take care of your health.',
            'from@example.com',
            [instance.user.email],
            fail_silently=False,
        )

@receiver(post_save, sender=Doctor)
def send_doctor_registration_email(sender, instance, created, **kwargs):
    if created:
        send_mail(
            'Welcome to Our Health Service',
            f'Hello Dr. {instance.user.full_name},\n\nThank you for registering as a doctor. We are excited to have you on board.',
            'from@example.com',
            [instance.user.email],
            fail_silently=False,
        )

