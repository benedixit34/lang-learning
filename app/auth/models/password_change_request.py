from django.conf import settings
from django.db import models
from django.utils import timezone


class PasswordChangeRequest(models.Model):
    token = models.CharField(max_length=64, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    validated_at = models.DateTimeField(null=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=15)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def has_been_validated(self):
        return True if self.validated_at else False
