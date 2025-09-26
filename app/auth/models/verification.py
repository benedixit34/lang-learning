from hashlib import sha256

from django.conf import settings
from django.db import models
from django.utils import timezone

from ..utils import generate_secure_code


class Verification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    has_been_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.id:
            self.expires_at = timezone.now() + timezone.timedelta(
                hours=1
            )  # Expires in 1 hour
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def generate_code(self) -> str:
        raw_code = generate_secure_code()
        self.code = sha256(raw_code.encode("utf-8")).hexdigest()
        return raw_code

    def verify_code(self, raw_code: str):
        if self.code == sha256(raw_code.encode("utf-8")).hexdigest():
            self.has_been_used = True
            self.save()
            return True
        return False
