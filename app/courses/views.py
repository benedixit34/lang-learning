from django.core.files.storage import FileSystemStorage
from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action


from app.courses.permissions import CanAccessLesson, IsInstructor, IsSubscribed, CanEnroll


from .mixins import SubscriptionMixin
from .models import (
    Course,
    CourseBundle,
    CourseBundleChoice,
    SpecialCourseBundle,
    Lesson,
    Section,
    UserCourseProgress,
    UserLessonCompletion,
)
from .serializers import (
    CourseBundleChoiceSerializer,
    CourseBundleReadSerializer,
    CourseBundleWriteSerializer,
    CourseReadSerializer,
    CourseWriteSerializer,
    LessonListReadSerializer,
    LessonRetrieveReadSerializer,
    LessonWriteSerializer,
    UserCourseProgressSerializer,
    UserLessonCompletionSerializer,
    VideoReadSerializer,
    VideoWriteSerializer,
)


from app.courses.utils import get_completed_level

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    lookup_field = "uuid"

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = serializer.save()
        read_serializer = CourseReadSerializer(course)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        return Course.objects.prefetch_related("instructors").all()


    @action(detail=True, methods=['get'], url_path="lessons/completed")
    def completed_lessons(self, request, uuid=None):
        course = self.get_object()
        user = request.user

        completed_ids = (
            UserLessonCompletion.objects
            .filter(user=user, lesson__course=course)
            .values_list('lesson_id', flat=True)
        )

        completed_lessons = Lesson.objects.filter(id__in=completed_ids).order_by("order")
        completed_lessons = completed_lessons.select_related('course', 'section')

        serializer = LessonListReadSerializer(completed_lessons, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

            
    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAuthenticated, IsAdminUser]

        return [permission() for permission in self.permission_classes]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CourseReadSerializer
        return CourseWriteSerializer


class LessonViewSet(viewsets.ModelViewSet):
    lookup_field = "uuid"

    def get_queryset(self):
        course_uuid = self.kwargs.get("course_uuid")
        course = get_object_or_404(Course, uuid=course_uuid)
        return course.lessons.all()

    
    def get_permissions(self):
        if self.action in ["list"]:
            self.permission_classes = [IsAuthenticated]
        elif self.action in ["create", "update", "partial_update", "destroy"]:
            self.permission_classes = [IsAdminUser]
        elif self.action in ["retrieve", "complete_lesson"]:
            self.permission_classes = [IsAuthenticated, CanAccessLesson, IsSubscribed]
        else:
            self.permission_classes = [IsAdminUser]
        return [perm() for perm in self.permission_classes]

    def get_serializer_class(self):
        if self.action in ["list"]:
            return LessonListReadSerializer
        elif self.action in ["retrieve"]:
            return LessonRetrieveReadSerializer
        return LessonWriteSerializer

    def create(self, request, course_uuid):
        request.data["course"] = course_uuid
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            course = serializer.validated_data["course"]
            order = course.lessons.count() + 1
            serializer.validated_data["order"] = order
            lesson = serializer.save()
        read_serializer = LessonRetrieveSerializer(lesson)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)
    

    @action(detail=True, methods=["post"], url_path="completed")
    def complete_lesson(self, request, *args, **kwargs):
        lesson = self.get_object()
        user_completion, created = UserLessonCompletion.objects.update_or_create(
            user=self.request.user,
            lesson=lesson,
            defaults={}
        )
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        serializer = UserLessonCompletionSerializer(user_completion)
        return Response(serializer.data, status=status_code)



class CourseBundleViewset(viewsets.ModelViewSet):
    queryset = CourseBundle.objects.all()
    lookup_field = "uuid"

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course_bundle = serializer.save()
        read_serializer = CourseBundleReadSerializer(course_bundle)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)


    @action(detail=True, methods=['get'], url_path='courses')
    def get_bundles_courses(self, request, uuid=None):
        bundle = self.get_object()
        courses = bundle.courses.all()
        serializer = CourseReadSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @action(detail=True, methods=['post'], url_path='enrol')
    def enrol_course_bundle(self, request, uuid=None):
        course_bundle = self.get_object()
        user = request.user
        if CourseBundleChoice.objects.filter(user=user, course_bundle=course_bundle).exists():
            return Response(
                {"detail": "You are already enrolled in this course bundle."},
                status=status.HTTP_400_BAD_REQUEST
            )
        choice = CourseBundleChoice.objects.create(user=user, course_bundle=course_bundle)
        serializer = CourseBundleChoiceSerializer(choice, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
                
    
    #check if the user is enrolled
    @action(detail=True, methods=['get'], url_path='enrolled')
    def enrolled(self, request, uuid=None):
        course_bundle = self.get_object()
        is_enrolled = CourseBundleChoice.objects.filter(user=request.user, course_bundle=course_bundle).exists()
        return Response({"enrolled": is_enrolled}, status=status.HTTP_200_OK)

    
    def get_permissions(self):
        if self.request.method in ["GET"]:
            self.permission_classes = [IsAuthenticated]
        elif self.action =="enrol_course_bundle":
            self.permission_classes = [IsAuthenticated, CanEnroll]
        elif self.request.method in ["POST", "PATCH", "DELETE"]:
            self.permission_classes = [IsAuthenticated, IsAdminUser]
        else:
            self.permission_classes = [IsAdminUser]

        return [permission() for permission in (self.permission_classes or [])]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CourseBundleReadSerializer
        return CourseBundleWriteSerializer