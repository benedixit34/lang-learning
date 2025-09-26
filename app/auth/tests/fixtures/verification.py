from hashlib import sha256

import pytest

from ...models import Verification


@pytest.fixture
def verification_data():
    return {
        "code": "567890",
    }


@pytest.fixture
def test_verification(verification_data, test_user):
    verification = Verification(user=test_user)
    verification.code = sha256(
        verification_data.get("code").encode("utf-8")
    ).hexdigest()
    verification.save()
    return verification


@pytest.fixture
def test_second_verification(test_user):
    verification = Verification(user=test_user)
    verification.code = sha256("999999".encode("utf-8")).hexdigest()
    verification.save()
    return verification
