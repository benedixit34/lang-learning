from django.contrib.auth import get_user_model

import factory

from ..models import Instructor

User = get_user_model()


class CustomUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "password")


class InstructorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Instructor

    user = factory.SubFactory(CustomUserFactory)
    bio = "Instructor Bio"
    profile_picture = "https://example.com/profile.png"
