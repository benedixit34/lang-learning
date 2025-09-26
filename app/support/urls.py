from rest_framework.routers import SimpleRouter

from .views import AppointmentViewSet, CourseViewSet

router = SimpleRouter(trailing_slash=False)
router.register(r"appointments", AppointmentViewSet, basename="appointments")
router.register(r"support-courses", CourseViewSet, basename="courses")


urlpatterns = router.urls
