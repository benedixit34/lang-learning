from django.contrib.auth import get_user_model
from django.core.mail import send_mail, BadHeaderError

from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from app.auth.models import Verification
from app.courses.utils import has_subscription



from .serializers import (
    ChangePasswordSerializer,
    UserReadSerializer,
    UserUpdateSerializer,
    UserWriteSerializer,
)

User = get_user_model()


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    lookup_field = "uuid"

    def create(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            read_serializer = UserReadSerializer(user)

            verification = Verification(user=user)
            raw_code = verification.generate_code()
            verification.save()

            email_content = (
                f"Welcome to AE Learning \n"
                f"Here is your verification code: {raw_code}.\n"
                f"Kindly complete your registration and dive into our world of innovative learning experience."
            )
            try:
                send_mail(
                    "Welcome to AE Learning",
                    email_content,
                    "learn@afroeuropean.uk",
                    [user.email],
                    fail_silently=False,
                )
                return Response(read_serializer.data, status=status.HTTP_201_CREATED)
            except (BadHeaderError, Exception) as e:
                return Response({"details": e}, status=status.HTTP_502_BAD_GATEWAY)
        except Exception as e:
            return Response({"details": e}, status=status.HTTP_500_INTERNAL_ERROR)

    def partial_update(self, request, uuid=None):
        if str(request.user.uuid) != uuid:
            return Response(
                {
                    "status": "error",
                    "code": status.HTTP_403_FORBIDDEN,
                    "message": "You can only update your own details.",
                },
            )
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

        # If validation fails, return the errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


        
    @action(detail=True, methods=["get"], url_path="subscribed")
    def subscribed(self, request, uuid=None):
        user = self.get_object()
        is_subscribed = has_subscription(user)
        return Response({"is_subscribed": is_subscribed}, status=status.HTTP_200_OK)

        
    def get_permissions(self):
        if self.request.method == "POST":
            self.permission_classes = [AllowAny]
        elif self.request.method in ["PATCH", "PUT"]:
            self.permission_classes = [IsAuthenticated]
        elif self.request.method == "GET" and self.action == "enrolled_course_bundle":
            self.permission_classes = [IsAuthenticated]

        return [permission() for permission in (self.permission_classes or [])]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return UserWriteSerializer
        elif self.request.method in ["PATCH", "PUT"]:
            return UserUpdateSerializer

        return UserReadSerializer


class ChangePasswordView(generics.UpdateAPIView):
   
    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("current_password")):
                return Response(
                    {
                        "status": "error",
                        "code": status.HTTP_400_BAD_REQUEST,
                        "message": "The current password supplied is wrong.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # set_password also hashes the password that the user will get

            self.object.set_password(serializer.data.get("password"))
            self.object.save()
            response = {
                "status": "success",
                "code": status.HTTP_200_OK,
                "message": "Password changed successfully",
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
