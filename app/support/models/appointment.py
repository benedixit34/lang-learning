from django.conf import settings
from django.db import models

from app.general.models import CreatedUpdated

from .course import Course


class Appointment(CreatedUpdated):
    fixed_time = models.DateTimeField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="appointments"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="appointments"
    )

    def __str__(self):
        return f"{self.course.title} appointment for {self.user.first_name} {self.user.last_name}"
