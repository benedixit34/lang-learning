from django.contrib import admin

# Register your models here.
from .models.verification import Verification
from .models.password_change_request import PasswordChangeRequest

admin.site.register(Verification)
admin.site.register(PasswordChangeRequest)
