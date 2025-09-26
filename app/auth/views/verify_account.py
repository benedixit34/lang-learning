from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ..models import Verification

User = get_user_model()


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_user_account(request):
    email = request.data.get("email")
    code = request.data.get("code")

    user = get_object_or_404(User, email=email)

    # descending: newest - oldest
    verification = (
        Verification.objects.filter(user=user, has_been_used=False)
        .order_by("-id")
        .first()
    )

    if verification is None:
        return Response(
            {"error": "Invalid or expired code"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if verification.verify_code(code) and not verification.is_expired():
        user.is_active = True
        user.save()

        return Response(
            {"success": "Account verified successfully"},
            status=status.HTTP_200_OK,
        )
    else:
        return Response(
            {
                "error": "Invalid or expired code. Use the most recent verification code sent."
            },
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def resend_verification_code(request):
    email = request.data.get("email")
    user = get_object_or_404(User, email=email)
    Verification.objects.filter(user=user).update(has_been_used=True)

    # send new verification code
    send_new_verification_code(user)
    return Response(
        {"success": "New verification code sent"},
        status=status.HTTP_201_CREATED,
    )


def send_new_verification_code(user):
    verification = Verification(user=user)
    raw_code = verification.generate_code()
    verification.save()
    send_mail(
        "Welcome to our app!",
        f"Here is your verification code: {raw_code}.",
        "learn@afroeuropean.uk",
        [user.email],
        fail_silently=False,
    )
