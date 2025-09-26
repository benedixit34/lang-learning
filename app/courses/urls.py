from django.urls import include, path
from rest_framework_nested import routers

from .views import (
    CourseBundleViewset,
    CourseViewSet,
    LessonViewSet,
    SectionViewSet,
    VideoViewSet,
)

router = routers.SimpleRouter(trailing_slash=False)

router.register(r"courses", CourseViewSet, basename="courses")
router.register(r"course-bundles", CourseBundleViewset, basename="course-bundles")

courses_router = routers.NestedSimpleRouter(router, r"courses", lookup="course")
courses_router.register(r"sections", SectionViewSet, basename="sections")

sections_router = routers.NestedSimpleRouter(courses_router, r"sections", lookup="section")
sections_router.register(r"lessons", LessonViewSet, basename="lessons")

lesson_router = routers.NestedSimpleRouter(sections_router, r"lessons", lookup="lesson")
lesson_router.register(r"videos", VideoViewSet, basename="videos")

urlpatterns = [
    path(r"", include(router.urls)),
    path(r"", include(courses_router.urls)),
    path(r"", include(sections_router.urls)),
    path(r"", include(lesson_router.urls)),
]

# /courses
# /courses/${id}
# /courses/${course_id}/lessons
# /courses/${course_id}/lessons/${lesson_id}
# /courses/${course_id}/lessons/${lesson_id}/videos
# /course-bundles/${course_bundle_id}
# /course-bundles/${course_bundle_id}/courses
# /course-bundle-select/${course_bundle_choice_id}  # New URL pattern for CourseBundleChoice
