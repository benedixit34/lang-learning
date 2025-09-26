import pytest


class TestCourseModel:
    @pytest.mark.django_db
    def test_str_method(self, course_factory):
        course = course_factory()
        assert str(course) == course.name


class TestLessonModel:
    @pytest.mark.django_db
    def test_str_method(self, lesson_factory):
        lesson = lesson_factory()
        assert str(lesson) == lesson.title


class TestVideoModel:
    @pytest.mark.django_db
    def test_str_method(self, video_factory):
        video = video_factory()
        assert str(video) == video.name


class TestUserVideoAccessModel:
    @pytest.mark.django_db
    def test_user_video_access(self, user_video_access_factory):
        access = user_video_access_factory()
        assert access.user == access.video.course.instructors.first().user
        assert access.access_count == 0
