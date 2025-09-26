from django.core.files.storage import FileSystemStorage
from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action


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
    LessonReadSerializer,
    LessonWriteSerializer,
    SectionReadSerializer,
    UserCourseProgressSerializer,
    UserLessonCompletionSerializer,
    VideoReadSerializer,
    VideoWriteSerializer,
)


from app.courses.utils import get_user_courses, has_subscription, \
    get_enrolled_lessons, get_user_videos, get_completed_level
from app.courses.permissions import lesson_permission, is_instructor

# from .tasks import upload_video_lesson

# Create your views here.

class CourseViewSet(SubscriptionMixin, viewsets.ModelViewSet):
    queryset = Course.objects.all()
    lookup_field = "uuid"

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = serializer.save()
        read_serializer = CourseReadSerializer(course)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        # bundle_uuid = self.kwargs["course_bundle_uuid"]

        # if bundle_uuid:
        #     return Course.objects.prefetch_related("bundles").filter(
        #         bundles__uuid=bundle_uuid
        #     )
        return Course.objects.prefetch_related("instructors").all()

    
        
    @action(detail=True, methods=['get'], url_path='level')
    def get_course_completion(self, request, uuid=None):
        course = self.get_object()
        completion_level = self.get_completed_level(user=self.request.user, course=course)

        course_progress, created = UserCourseProgress.objects.update_or_create(
            user=self.request.user,
            course=course,
            defaults={'completion_level': completion_level}
        )

        serializer = UserCourseProgressSerializer(course_progress)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(serializer.data, status=status_code)


    @action(detail=True, methods=['get'], url_path='enrolled')
    def enrolled(self, request, uuid=None):
        course = self.get_object()
        is_enrolled = get_user_courses(user= request.user).filter(id=course.id).exists()
        return Response({"enrolled": is_enrolled}, status=status.HTTP_200_OK)


    @action(detail=True, methods=['get'], url_path="completed-lessons")
    def completed_lessons(self, request, uuid=None):
        course = self.get_object()
        all_courses = get_user_courses(request.user)

        if course not in all_courses:
            raise PermissionDenied("You are not enrolled in this course.")

        completed_lessons = Lesson.objects.filter(
            course=course,
            userlessoncompletion__user=request.user
         ).order_by("order")

        serializer = LessonReadSerializer(completed_lessons, many=True)
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


class LessonViewSet(SubscriptionMixin, viewsets.ModelViewSet):
    lookup_field = "uuid"

    def get_queryset(self):
        if 'sections_uuid' in self.kwargs:
            section_uuid = self.kwargs["sections_uuid"]
            return get_enrolled_lessons(self.request.user).filter(section__uuid=section_uuid)
        return get_enrolled_lessons(self.request.user)
    

    def create(self, request, course_uuid):
        request.data["course"] = course_uuid
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            course = serializer.validated_data["course"]
            order = course.lessons.count() + 1
            serializer.validated_data["order"] = order
            lesson = serializer.save()
        read_serializer = LessonReadSerializer(lesson)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)
    

    @action(detail=True, methods=["post"], url_path="completed")
    def complete_lesson(self, request, *args, **kwargs):
        lesson = self.get_object()
        has_subscription(request.user)
        user_completion, created = UserLessonCompletion.objects.update_or_create(
            user=self.request.user,
            lesson=lesson,
            defaults={}
        )
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        serializer = UserLessonCompletionSerializer(user_completion)
        return Response(serializer.data, status=status_code)


    def retrieve(self, request, *args, **kwargs):
        lesson = self.get_object()
        lesson_permission(lesson=lesson, user=request.user)
        return super().retrieve(request, *args, **kwargs)

            


    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [IsAuthenticated]
        elif self.request.method == "POST" and self.action == "complete_lesson":
            self.permission_classes = [IsAuthenticated]
        elif self.request.method in ["DELETE"]:
            self.permission_classes = [IsAuthenticated, IsAdminUser]
        else:
            self.permission_classes = [IsAdminUser]

        return [permission() for permission in (self.permission_classes or [])]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return LessonReadSerializer
        return LessonWriteSerializer


class VideoViewSet(SubscriptionMixin, viewsets.ModelViewSet):
    def get_queryset(self):
        lesson_uuid = self.kwargs["lesson_uuid"]
        return get_user_videos(self.request.user).filter(lesson__uuid=lesson_uuid)


    def create(self, request, course_uuid, lesson_uuid):
        # request.data["lesson"] = lesson_uuid
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        video_file = serializer.validated_data.pop("video_file")
        image_file = serializer.validated_data.pop("image_file")

        fs = FileSystemStorage()
        video_file_name = fs.save(video_file.name, video_file)
        video_file_path = fs.path(video_file_name)

        image_file_name = fs.save(image_file.name, image_file)
        image_file_path = fs.path(image_file_name)

        video_metadata = {
            "file_path": video_file_path,
            "file_name": video_file_name,
            **serializer.validated_data,
        }

        image_metadata = {"file_path": image_file_path, "file_name": image_file_name}

        # upload_video_lesson.delay(video_metadata, image_metadata)
        return Response({"success": "Video has been queued for upload!"})

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAuthenticated, IsAdminUser]

        return [permission() for permission in self.permission_classes]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return VideoReadSerializer
        return VideoWriteSerializer


class CourseBundleViewset(SubscriptionMixin, viewsets.ModelViewSet):
    queryset = CourseBundle.objects.all()
    lookup_field = "uuid"

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course_bundle = serializer.save()
        read_serializer = CourseBundleReadSerializer(course_bundle)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)


    @action(detail=False, methods=['get'], url_path='courses')
    def get_bundles_courses(self, request, uuid=None):
        bundle = self.get_object()
        has_bundle = CourseBundleChoice.objects.filter(
            user=request.user, course_bundle=bundle
        ).exists()

        if not has_bundle:
            raise PermissionDenied("You do not have access to this course bundle.")
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

        if not user.is_staff or not is_instructor(user):
            existing_choices = CourseBundleChoice.objects.filter(user=user).select_related("course_bundle")


            special_bundle_ids = set(
                SpecialCourseBundle.objects.filter(
                    course_bundle__in=[choice.course_bundle for choice in existing_choices]
                ).values_list("course_bundle_id", flat=True)
            )

            non_special_choices = [choice for choice in existing_choices if choice.course_bundle.id not in special_bundle_ids]

            courses_to_check = Course.objects.filter(
                coursebundle__in=[choice.course_bundle for choice in non_special_choices]
            ).distinct()


            incomplete_course = next(
                (course for course in courses_to_check if get_completed_level(user, course) < 100),
                None
            )
            if incomplete_course:
                raise PermissionDenied(
                    f"You must complete {incomplete_course.name} before enrolling in a new course bundle."
                )

   
        choice = CourseBundleChoice.objects.create(user=user, course_bundle=course_bundle)
        serializer = CourseBundleChoiceSerializer(choice, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
                

    
    #check if the user is subscribed
    @action(detail=True, methods=['get'], url_path='subscribed')
    def subscribed(self, request, uuid=None):
        is_subscribed = has_subscription(request.user)
        return Response({"subscribed": is_subscribed}, status=status.HTTP_200_OK)
       
    
    #check if the user is enrolled
    @action(detail=True, methods=['get'], url_path='enrolled')
    def enrolled(self, request, uuid=None):
        course_bundle = self.get_object()
        is_enrolled = CourseBundleChoice.objects.filter(user=request.user, course_bundle=course_bundle).exists()
        return Response({"enrolled": is_enrolled}, status=status.HTTP_200_OK)

    
    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [IsAuthenticated]
        elif self.request.method == "POST" and self.action == "enrol_course_bundle":
            self.permission_classes = [IsAuthenticated]
        elif self.request.method == "DELETE" and self.action == "leave_course_bundle":
            self.permission_classes = [IsAuthenticated]
        elif self.request.method in ["PATCH"]:
            self.permission_classes = [IsAuthenticated, IsAdminUser]
        else:
            self.permission_classes = [IsAdminUser]

        return [permission() for permission in (self.permission_classes or [])]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CourseBundleReadSerializer
        return CourseBundleWriteSerializer


class SectionViewSet(viewsets.ModelViewSet):
    lookup_field = "uuid"

    def get_queryset(self):
        course_uuid = self.kwargs["course_uuid"]
        return Section.objects.prefetch_related("lessons").filter(
            course__uuid=course_uuid
        )

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAuthenticated, IsAdminUser]

        return [permission() for permission in self.permission_classes]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return SectionReadSerializer