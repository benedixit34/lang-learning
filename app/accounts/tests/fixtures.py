from django.contrib.auth import get_user_model

import pytest

from .factories import CustomUserFactory, InstructorFactory

User = get_user_model()


@pytest.fixture
def user_data():
    return {
        "first_name": "Test",
        "last_name": "Password",
        "email": "testpassword@gmail.com",
        "password": "Nicetry1$$$$",
    }


@pytest.fixture
def test_user(user_data):
    return User.objects.create_user(**user_data)


@pytest.fixture
def user():
    return CustomUserFactory()


@pytest.fixture
def instructor_factory():
    return InstructorFactory()
