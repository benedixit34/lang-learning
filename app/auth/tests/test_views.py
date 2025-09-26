from django.urls import reverse

import pytest

from app.accounts.serializers import UserReadSerializer

from ...auth.models import Verification


@pytest.mark.django_db
class TestLogin:
    url = reverse("auth_login")

    def test_valid_login(self, api_client, test_user, user_data):
        data = {
            "email": user_data.get("email"),
            "password": user_data.get("password"),
        }
        response = api_client.post(self.url, data, format="json")
        assert response.status_code == 200

        expected_keys = ["authentication", "user"]
        assert all(key in response.data for key in expected_keys)

        expected_authentication_keys = ["access_token", "refresh_token"]
        assert all(
            key in response.data["authentication"]
            for key in expected_authentication_keys
        )

        assert response.data["user"] == UserReadSerializer(test_user).data

    def test_signin_with_invalid_credentials(self, api_client, test_user, user_data):
        data = {"email": user_data.get("email"), "password": "wrongpassword"}
        response = api_client.post(self.url, data, format="json")
        assert response.status_code == 401
        assert response.data == {"Incorrect email or password."}


@pytest.mark.django_db
class TestCodeVerification:
    url = reverse("verify_user_account")

    def test_successful_verification(
        self, api_client, verification_data, test_user, test_verification
    ):
        data = {
            "email": test_user.email,
            "code": verification_data.get("code"),
        }
        assert not test_user.is_active
        response = api_client.post(self.url, data, format="json")
        assert response.status_code == 200
        test_user.refresh_from_db()
        assert test_user.is_active
        test_verification.refresh_from_db()
        assert test_verification.has_been_used
        assert response.data == {"success": "Account verified successfully"}

    def test_invalid_code(self, api_client, test_verification):
        data = {"email": test_verification.user.email, "code": "123456"}

        response = api_client.post(self.url, data, format="json")
        assert response.status_code == 404

    def test_verification_not_found(self, api_client, test_user):
        data = {"email": test_user.email, "code": 123456}
        response = api_client.post(self.url, data, format="json")
        assert response.status_code == 404

    def test_any_unused_verification_code_works(
        self,
        api_client,
        verification_data,
        test_second_verification,
        test_verification,
    ):
        data = {"email": test_second_verification.user.email, "code": "999999"}
        response = api_client.post(self.url, data, format="json")
        assert response.status_code == 200
        assert response.data == {"success": "Account verified successfully"}

        data["code"] = verification_data.get("code")
        response = api_client.post(self.url, data, format="json")
        assert response.status_code == 200


@pytest.mark.django_db
class TestResendVerificationCode:
    url = reverse("resend_verification_code")

    def test_other_codes_become_inactive(
        self, api_client, test_second_verification, test_verification
    ):
        data = {"email": test_verification.user.email}
        assert not test_second_verification.has_been_used
        assert not test_verification.has_been_used
        response = api_client.post(self.url, data, format="json")
        test_second_verification.refresh_from_db()
        test_verification.refresh_from_db()

        assert test_second_verification.has_been_used
        assert test_verification.has_been_used

        assert response.status_code == 201

    def test_new_code_generated(self, api_client, test_verification):
        data = {"email": test_verification.user.email}
        user_verification = Verification.objects.filter(
            user=test_verification.user
        ).count()
        assert user_verification == 1
        response = api_client.post(self.url, data, format="json")

        user_verification = Verification.objects.filter(
            user=test_verification.user
        ).count()
        assert user_verification == 2
