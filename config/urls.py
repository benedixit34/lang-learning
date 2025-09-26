from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenRefreshView

API_PREFIX = "api/v1/"

urlpatterns = [
    path("admin/", admin.site.urls),
    path(f"{API_PREFIX}users/", include("app.accounts.urls")),
    path(f"{API_PREFIX}auth/", include("app.auth.urls")),
    path(f"{API_PREFIX}", include("app.support.urls")),
    path(f"{API_PREFIX}", include("app.courses.urls")),
    path(f"{API_PREFIX}pay/", include("drf_stripe.urls")),
    ## documentation related endpoints
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Optional UI:
    path(
        "api/docs",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        f"{API_PREFIX}token/refresh/", TokenRefreshView.as_view(), name="token_refresh"
    ),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
