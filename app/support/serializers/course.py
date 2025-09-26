from rest_framework import serializers

from ..models import Course


class CourseReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ("uuid", "title", "created_at", "updated_at")
