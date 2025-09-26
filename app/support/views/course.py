from rest_framework import viewsets

from ..models import Course
from ..serializers import CourseReadSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    lookup_field = "uuid"
    serializer_class = CourseReadSerializer
