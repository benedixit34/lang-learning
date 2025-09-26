from django.contrib import admin

# Register your models here.
from .models import CustomUser, Instructor, Subscriber

admin.site.register(CustomUser)
admin.site.register(Instructor)
admin.site.register(Subscriber)
