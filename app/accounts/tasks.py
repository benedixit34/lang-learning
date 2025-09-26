from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from celery import shared_task

from app.auth.models import Verification

User = get_user_model()


# @shared_task
# def send_verification_email(user_email: str):
#     user = User.objects.get(email=user_email)
