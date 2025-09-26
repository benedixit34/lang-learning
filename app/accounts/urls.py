from django.urls import path

from rest_framework.routers import SimpleRouter

from .views import ChangePasswordView, UserViewSet

router = SimpleRouter(trailing_slash=False)
router.register(r"", UserViewSet, basename="users")


urlpatterns = [
    path("change-password", ChangePasswordView.as_view(), name="change-password")
]
urlpatterns += router.urls
