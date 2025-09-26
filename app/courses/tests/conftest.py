import pytest
from pytest_factoryboy import register

from .factories import (
    CourseFactory,
    LessonFactory,
    UserVideoAccessFactory,
    VideoFactory,
)

register(VideoFactory)
register(CourseFactory)
register(LessonFactory)
register(UserVideoAccessFactory)


@pytest.fixture
def video(factory_boy, course):
    return factory_boy(VideoFactory, course=course)
