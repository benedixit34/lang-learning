from django.contrib.auth import get_user_model

import pytest

User = get_user_model()


@pytest.mark.django_db
class TestCustomUserModel:
    def test_str_method(self, user):
        assert str(user) == user.email


class TestInstructorModel:
    @pytest.mark.django_db
    def test_str_method(self, instructor_factory):
        instructor = instructor_factory
        assert (
            str(instructor)
            == f"{instructor.user.first_name} {instructor.user.last_name}"
        )


@pytest.mark.django_db
class TestUserManager:
    def test_create_superuser(self, user_data):
        user = User.objects.create_superuser(**user_data)
        assert user.is_staff
        assert user.is_superuser

    def test_create_user(self, user_data):
        user = User.objects.create_user(**user_data)

        assert user.email == user_data.get("email")
        assert user.check_password(user_data.get("password"))

    def test_user_with_no_email_raises_error(self, user_data):
        del user_data["email"]

        with pytest.raises(ValueError):
            User.objects.create_user(**user_data)
