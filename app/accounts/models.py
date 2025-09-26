import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from .manager import UserManager
from .utils import generate_referral_code


# Custom user model extending Django's AbstractUser, including subscription fields
class CustomUser(AbstractUser):
    username = None
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=False)
    referral_code = models.CharField(max_length=15, unique=True, blank=True, null=True)

    objects = UserManager()
    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        if not self.referral_code:  # Only generate code if it doesn't exist
            self.referral_code = self.generate_unique_referral_code()
        super().save(*args, **kwargs)

    def generate_unique_referral_code(self):
        code = generate_referral_code(15)
        while CustomUser.objects.filter(referral_code=code).exists():
            code = generate_referral_code(15)
        return code


# Model representing instructors with user profile linkage
class Instructor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="instructor_profile",
    )
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"



class Subscriber(models.Model):
    user = models.ForeignKey( settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriber")
    is_subscribed=models.BooleanField(default=False)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()