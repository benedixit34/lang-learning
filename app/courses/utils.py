import cloudinary
import cloudinary.uploader


from app.courses.models import Lesson, CourseBundleChoice, \
    SpecialCourseBundle, UserLessonCompletion, Course, Video
from app.accounts.models import Subscriber
from app.courses.stripe_payments import get_user_active_subscriptions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status


def upload_image_to_cloudinary(image_file):
    res = cloudinary.uploader.upload(image_file)
    return res["secure_url"]


def upload_video_to_cloudinary(video_file):
    res = cloudinary.uploader.upload_large(video_file, resource_type="video")
    return res["secure_url"]


def cleanup_files(fs, *file_paths):
    for path in file_paths:
        fs.delete(path)


def has_subscription(user):
    subs = get_user_active_subscriptions(user)
    return bool(subs) or Subscriber.objects.filter(user=user, is_subscribed=True).exists()


def access_special_course(user, product_id):
    subs = get_user_active_subscriptions(user)   
    subscribed_products = [sub.product_id for sub in subs]
    if product_id not in subscribed_products:
        raise PermissionDenied("You are not subscribed to this product")
    
    return True



def get_user_lessons(user):
    if not has_subscription(user):
        raise PermissionDenied("You need an active subscription to access lessons.")

    bundle_choices = CourseBundleChoice.objects.filter(user=user).select_related("course_bundle")
    bundles = [choice.course_bundle for choice in bundle_choices]
    special_bundles = SpecialCourseBundle.objects.filter(course_bundle__in=bundles)

    for special_bundle in special_bundles:
        access_special_course(user, special_bundle.product_id)

    return Lesson.objects.filter(course__coursebundle__in=bundles).distinct()



def get_user_videos(user):
    lessons = get_user_lessons(user)
    return Video.objects.filter(lesson__in=lessons).order_by("created_at")





def get_user_courses(user):
    bundle_choices = CourseBundleChoice.objects.filter(user=user).values_list("course_bundle", flat=True)
    return Course.objects.filter(coursebundle__in=bundle_choices).distinct()


def get_enrolled_lessons(user):
    courses = get_user_courses(user)
    if not courses.exists():
        raise PermissionDenied("Please select a course bundle.")
    return Lesson.objects.filter(course__in=courses)


def get_completed_level(user, course):
    lessons = get_enrolled_lessons(user).filter(course=course)
    total_lessons = lessons.count()
    if total_lessons == 0:
        return 0

    completed = UserLessonCompletion.objects.filter(user=user, lesson__in=lessons).count()
    return round((completed / total_lessons) * 100, 2)
