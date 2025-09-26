from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from app.courses.models import (
    Course, CourseBundle, CourseBundleChoice, SpecialCourseBundle,
    Lesson, Section, UserLessonCompletion, UserCourseProgress
)
from app.courses.utils import get_completed_level

User = get_user_model()

class CoursesAPITestCase(APITestCase):
    def setUp(self):
        # Create users
        self.user = User.objects.create_user(username="user1", email="user1@test.com", password="pass1234")
        self.staff_user = User.objects.create_superuser(username="admin", email="admin@test.com", password="admin1234")

        # Create a course and bundle
        self.course = Course.objects.create(name="Test Course")
        self.course_bundle = CourseBundle.objects.create(name="Test Bundle")
        self.course_bundle.courses.add(self.course)

        # Section and lesson
        self.section = Section.objects.create(name="Test Section", course=self.course)
        self.lesson = Lesson.objects.create(title="Lesson 1", course=self.course, order=1, section=self.section)

        # Special bundle
        self.special_bundle = SpecialCourseBundle.objects.create(course_bundle=self.course_bundle)

    def test_course_enrollment(self):
        url = reverse("coursebundle-enrol-course-bundle", args=[self.course_bundle.uuid])
        self.client.force_authenticate(user=self.user)

        # Enroll user
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CourseBundleChoice.objects.filter(user=self.user, course_bundle=self.course_bundle).exists())

        # Duplicate enrollment
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_course_bundle_enrolled_endpoint(self):
        url = reverse("coursebundle-enrolled", args=[self.course_bundle.uuid])
        self.client.force_authenticate(user=self.user)

        # Not enrolled yet
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["enrolled"])

        # Enroll and check
        CourseBundleChoice.objects.create(user=self.user, course_bundle=self.course_bundle)
        response = self.client.get(url)
        self.assertTrue(response.data["enrolled"])

    def test_subscribed_endpoint(self):
        url = reverse("coursebundle-subscribed", args=[self.course_bundle.uuid])
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("subscribed", response.data)

    def test_course_completion_level(self):
        url = reverse("course-get-course-completion", args=[self.course.uuid])
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("completion_level", response.data)

    def test_completed_lessons_endpoint(self):
        url = reverse("course-completed-lessons", args=[self.course.uuid])
        self.client.force_authenticate(user=self.user)

        # User not enrolled
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Enroll user and mark lesson completed
        CourseBundleChoice.objects.create(user=self.user, course_bundle=self.course_bundle)
        UserLessonCompletion.objects.create(user=self.user, lesson=self.lesson)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_lesson_completion(self):
        url = reverse("lesson-complete-lesson", args=[self.lesson.uuid])
        self.client.force_authenticate(user=self.user)

        # Complete lesson
        response = self.client.post(url)
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])
        self.assertTrue(UserLessonCompletion.objects.filter(user=self.user, lesson=self.lesson).exists())

    def test_video_access_queryset(self):
        from app.courses.utils import get_user_videos
        # Simulate a video for the lesson
        from app.courses.models import Video
        video = Video.objects.create(name="Video 1", lesson=self.lesson)
        self.client.force_authenticate(user=self.user)

        allowed_videos = get_user_videos(self.user).filter(lesson=self.lesson)
        self.assertIn(video, allowed_videos)

    def test_lesson_retrieve_permission(self):
        from rest_framework.exceptions import PermissionDenied
        self.client.force_authenticate(user=self.user)

        # Should raise PermissionDenied if previous lessons incomplete
        # First lesson, should pass
        url = reverse("lesson-detail", args=[self.lesson.uuid])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_bundles_courses_permission(self):
        url = reverse("coursebundle-get-bundles-courses", args=[self.course_bundle.uuid])
        self.client.force_authenticate(user=self.user)

        # Not enrolled → should raise PermissionDenied
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Enroll and test
        CourseBundleChoice.objects.create(user=self.user, course_bundle=self.course_bundle)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
