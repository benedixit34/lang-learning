import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def api_client_test(test_user):
    api_client = APIClient()
    api_client.force_authenticate(test_user)
    api_client.forced_user = test_user
    return api_client
