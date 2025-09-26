import os

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils import timezone

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from ..models import PasswordChangeRequest
from ..serializers.forgot_password import (
    CreateChangePasswordRequestSerializer,
    ResetPasswordSerializer,
)
from ..utils import generate_password_reset_token

User = get_user_model()


@extend_schema(
    request=CreateChangePasswordRequestSerializer,  # What the frontend should pass
    description="Endpoint to create a change password request.",
    parameters=[
        OpenApiParameter(
            name="email", type=str, description="User email", required=True
        ),
        OpenApiParameter(
            name="domain",
            type=str,
            description="Domain that is hitting this endpoint",
            required=True,
        ),
    ],
)
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def create_change_password_request(request):
    serializer = CreateChangePasswordRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.data.get("email")
    domain = serializer.data.get("domain")

    user = get_object_or_404(User, email=email)
    token = generate_password_reset_token(length=64)

    PasswordChangeRequest.objects.create(token=token, user=user)

    # send email
    password_reset_url = f"{domain}reset-password?email={email}&token={token}"
    email_content = (
        f"Let's reset your password and get you back to learning \n"
        f"Password reset url = {password_reset_url}.\n"
        f"If you did not ask to reset your password you may want to review your recent account access for any unusual activity."
    )
    send_mail(
        "Complete your password reset request",
        email_content,
        "learn@afroeuropean.uk",
        [user.email],
        fail_silently=False,
    )
    return Response(
        {
            "status": "success",
            "code": status.HTTP_200_OK,
            "message": "Email to reset password has been sent.",
        },
        status=status.HTTP_200_OK,
    )


@extend_schema(
    request=ResetPasswordSerializer,
    description="Endpoint to reset password.",
    parameters=[
        OpenApiParameter(
            name="email", type=str, description="User email", required=True
        ),
        OpenApiParameter(
            name="token",
            type=str,
            description="Token that was passed when forgot password was initiated",
            required=True,
        ),
    ],
)
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def reset_password(request):
    serializer = ResetPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.data.get("email")
    token = serializer.data.get("token")
    new_password = serializer.data.get("password")

    user = get_object_or_404(User, email=email)
    time_now = timezone.now()
    password_request = (
        PasswordChangeRequest.objects.filter(
            user=user, created_at__lte=time_now, expires_at__gte=time_now
        )
        .order_by("-id")
        .first()
    )
    if password_request is None:
        return Response(
            {
                "status": "error",
                "code": status.HTTP_400_BAD_REQUEST,
                "message": "Token has most likely expired. Request a new token.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if password_request.has_been_validated():
        return Response(
            {
                "status": "error",
                "code": status.HTTP_400_BAD_REQUEST,
                "message": "This token has already been validated.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    token_match = password_request.token == token
    if not token_match:
        return Response(
            {
                "status": "error",
                "code": status.HTTP_400_BAD_REQUEST,
                "message": "Invalid token provided. Use the most recent token sent to your email",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    user.set_password(new_password)
    user.save()
    password_request.validated_at = time_now
    password_request.save()
    response = {
        "status": "success",
        "code": status.HTTP_200_OK,
        "message": "Password has been reset successfully.",
    }
    return Response(response)
