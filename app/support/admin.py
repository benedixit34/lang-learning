from django.contrib import admin

from .models import Appointment, Course

# Register your models here.

admin.site.register(Appointment)
admin.site.register(Course)
