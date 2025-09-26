from django.db import models

from app.general.models import CreatedUpdated


class Course(CreatedUpdated):
    title = models.CharField(max_length=60)

    def __str__(self):
        return f"{self.title}"
