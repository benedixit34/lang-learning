import pytest

from ..backends import EmailBackend


@pytest.mark.django_db
class TestEmailBackend:
    def test_authenticate_valid_user(self, test_user, user_data, request_factory):
        backend = EmailBackend()
        request = request_factory.post("/login/")

        user = backend.authenticate(
            request, email=user_data["email"], password=user_data["password"]
        )
        assert user is not None
        assert user.email == user_data["email"]

    def test_authenticate_invalid_password(self, test_user, user_data, request_factory):
        backend = EmailBackend()
        request = request_factory.post("/login/")

        user = backend.authenticate(
            request, email=user_data["email"], password="wrongpassword"
        )
        assert user is None

    def test_authenticate_nonexistent_user(self, request_factory):
        backend = EmailBackend()
        request = request_factory.post("/login/")

        user = backend.authenticate(
            request, email="nonexistent@example.com", password="password"
        )
        assert user is None

    def test_get_user_valid_id(self, test_user):
        backend = EmailBackend()

        user = backend.get_user(test_user.id)
        assert user is not None
        assert user.email == test_user.email

    def test_get_user_invalid_id(self):
        backend = EmailBackend()

        user = backend.get_user(9999)
        assert user is None
