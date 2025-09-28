from app.accounts.models import Instructor
from rest_framework.permissions import BasePermission
from app.courses.utils import has_subscription, lesson_permission, get_completed_level
from app.courses.models import SpecialCourseBundle, CourseBundleChoice


class CanAccessLesson(BasePermission):
    def has_object_permission(self, request, view, obj):
        return lesson_permission(lesson=obj, user=request.user)


class IsInstructor(BasePermission):
    def has_permission(self, request, view):
        return Instructor.objects.filter(user=request.user).exists()


class IsSubscribed(BasePermission):
    def has_permission(self, request, view):
        return has_subscription(request.user)
    

class CanEnroll(BasePermission):


    def has_permission(self, request, view):
        user = request.user
       

        course_bundle_id = view.kwargs.get("uuid")
        if not course_bundle_id:
            return False

        try:
            if SpecialCourseBundle.objects.filter(course_bundle__uuid=course_bundle_id).exists():
                return True
        except SpecialCourseBundle.DoesNotExist:
            pass

        try:
            bundle_choice = CourseBundleChoice.objects.get(
                user=user, course_bundle__uuid=course_bundle_id
            )
            
        except CourseBundleChoice.DoesNotExist:
            return True
        for course in bundle_choice.course_bundle.courses.all():
            if get_completed_level(user, course) < 100:
                return True
        return False
