from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers


class CreateChangePasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    domain = serializers.URLField()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField()
    password = serializers.CharField(validators=[validate_password])
    confirm_password = serializers.CharField(
        validators=[validate_password], write_only=True
    )

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs
