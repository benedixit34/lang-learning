from django.contrib.auth import get_user_model
from django.urls import reverse

import pytest
from rest_framework import status

from ..serializers import UserReadSerializer

pytestmark = pytest.mark.django_db
User = get_user_model()


class TestCreateUser:
    endpoint = reverse("users-list")

    def test_create_user(self, api_client, user_data):
        response = api_client.post(self.endpoint, user_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

        for key in user_data:
            if key == "password":
                assert response.data.get(key) is None
                continue
            assert response.data.get(key) == user_data[key]

    def test_read_users(self, api_client_test, test_user):
        response = api_client_test.get(self.endpoint, format="json")
        qs = User.objects.all()
        assert response.status_code == status.HTTP_200_OK

        assert response.data.get("results") == UserReadSerializer(qs, many=True).data
