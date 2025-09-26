from django.urls import path

from .views import (
    LoginView,
    create_change_password_request,
    resend_verification_code,
    reset_password,
    verify_user_account,
)

urlpatterns = [
    path("login", LoginView.as_view(), name="auth_login"),
    path("verify-user", verify_user_account, name="verify_user_account"),
    path(
        "resend-verification-code",
        resend_verification_code,
        name="resend_verification_code",
    ),
    path(
        "forgot-password-request",
        create_change_password_request,
        name="create_change_password_request",
    ),
    path("reset-password", reset_password, name="reset_password"),
]
