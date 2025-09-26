from django.contrib.auth import authenticate, get_user_model

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers.login import LoginSerializer
from ..utils import get_user_auth_data

User = get_user_model()


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @staticmethod
    def post(request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            email=serializer.validated_data.get("email"),
            password=serializer.validated_data.get("password"),
        )
        if not user:
            return Response(
                {"Incorrect email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if user.is_active == False:
            return Response(
                {"Account hasn't been verified. Please, verify your account first."},
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response(get_user_auth_data(user, request), status=status.HTTP_200_OK)
