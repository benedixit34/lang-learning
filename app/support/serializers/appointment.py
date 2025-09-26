from rest_framework import serializers

from ..models import Appointment, Course
from .course import CourseReadSerializer


class AppointmentReadSerializer(serializers.ModelSerializer):
    course = CourseReadSerializer()

    class Meta:
        model = Appointment
        fields = ("uuid", "fixed_time", "user", "course", "created_at", "updated_at")


# serializer = UserUpdatePinSerializer(
#             data=request.data, context={"request": request}
#         )
class AppointmentWriteSerializer(serializers.ModelSerializer):
    course = serializers.UUIDField(write_only=True)

    class Meta:
        model = Appointment
        fields = ("fixed_time", "course")

    def create(self, validated_data):
        user = self.context.get("request").user
        course = validated_data.pop("course")
        appointment = Appointment.objects.create(
            course=course, user=user, **validated_data
        )
        return appointment

    def validate_course(self, value):
        try:
            return Course.objects.get(uuid=value)
        except Course.DoesNotExist:
            raise serializers.ValidationError(
                f"Course with UUID {value} does not exist."
            )
