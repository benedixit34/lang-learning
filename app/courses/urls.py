from django.urls import include, path
from rest_framework_nested import routers

from .views import (
    CourseBundleViewset,
    CourseViewSet,
    LessonViewSet,
)

# Main routers
router = routers.SimpleRouter(trailing_slash=False)
router.register(r"courses", CourseViewSet, basename="courses")
router.register(r"course-bundles", CourseBundleViewset, basename="course-bundles")

# Nested routers for courses -> lessons (with section_id in URL, but not a SectionViewSet)
courses_router = routers.NestedSimpleRouter(router, r"courses", lookup="course")
courses_router.register(
    r"lessons",
    LessonViewSet,
    basename="section-lessons"
)



# Combine all routes
urlpatterns = [
    path("", include(router.urls)),
    path("", include(courses_router.urls)),
]