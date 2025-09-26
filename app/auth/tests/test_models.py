from django.utils import timezone

import pytest

from ...auth.models import Verification


@pytest.mark.django_db
class TestVerification:
    def test_expires_at_saved_correctly(self, test_verification):
        assert test_verification.expires_at > timezone.now() + timezone.timedelta(
            minutes=59
        )

    def test_has_been_used(self, test_user):
        verification = Verification(user=test_user)
        raw_code = verification.generate_code()
        verification.save()

        verification.verify_code(raw_code)

        assert verification.has_been_used == True

    def test_code_checking(self, test_user):
        verification = Verification(user=test_user)
        raw_code = verification.generate_code()
        verification.save()

        assert verification.verify_code(raw_code)

    def test_invalid_code(self, test_verification):
        assert test_verification.verify_code("123456") == False

    def test_is_expired(self, test_verification):
        test_verification.expires_at = timezone.now() - timezone.timedelta(seconds=5)
        test_verification.save()
        test_verification.refresh_from_db()
        assert test_verification.is_expired()
