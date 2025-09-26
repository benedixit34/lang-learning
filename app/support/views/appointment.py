from django.core.mail import send_mail

from rest_framework import status, viewsets
from rest_framework.response import Response

from ..models import Appointment
from ..serializers import AppointmentReadSerializer, AppointmentWriteSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    lookup_field = "uuid"

    def get_queryset(self):
        return Appointment.objects.select_related("course").filter(
            user=self.request.user
        )

    def create(self, request):
        serializer = AppointmentWriteSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        appointment = serializer.save()
        user = request.user
        read_serializer = AppointmentReadSerializer(appointment)
        fixed_time = appointment.fixed_time

        appointment_date = fixed_time.strftime(
            "%A, %B %d, %Y"
        )  # e.g., "Sunday, March 16, 2025"
        appointment_time = fixed_time.strftime("%I:%M %p")

        # send email
        email_content = (
            f"Customer {user.first_name} {user.last_name} with email {user.email} is requesting support in {appointment.course.title} \n"
            f"They would like to have the appointment on {appointment_date} at {appointment_time}.\n"
            f"Please schedule a Google meeting for that user at the time specified."
        )
        send_mail(
            "Homework Support Request",
            email_content,
            "learn@afroeuropean.uk",
            ["support@afroeuropean.uk"],
            fail_silently=False,
        )
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)
