from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers

from .models import Instructor

User = get_user_model()


class UserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("uuid", "first_name", "last_name", "email", "referral_code")


class UserWriteSerializer(serializers.ModelSerializer):
    password = serializers.CharField(validators=[validate_password], write_only=True)
    referral_code = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "referral_code", "password")

    def create(self, validated_data):
        referral_code = validated_data.pop("referral_code", None)
        if referral_code:
            try:
                user = User.objects.get(referral_code=referral_code)
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid referral code.")

        return User.objects.create_user(**validated_data)


class InstructorReadSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Instructor
        fields = ("email", "full_name", "profile_picture", "created_at", "updated_at")
    
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    password = serializers.CharField(validators=[validate_password])

    def validate(self, attrs):
        if attrs["password"] == attrs["current_password"]:
            raise serializers.ValidationError(
                {
                    "password": "Your new password should be different from your current one."
                }
            )

        return attrs


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name")

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.save()
        return instance
