import cloudinary
import cloudinary.uploader


from app.courses.models import Lesson, CourseBundleChoice, \
    SpecialCourseBundle, UserLessonCompletion, Course
from app.accounts.models import Subscriber
from app.courses.stripe_payments import get_user_active_subscriptions
from rest_framework.exceptions import PermissionDenied



from django.utils import timezone
from django.utils.timesince import timesince
from datetime import timedelta
from rest_framework.exceptions import PermissionDenied
from app.courses.models import Lesson, UserLessonCompletion


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
    subscribed_products = [sub['product'] for sub in subs]
    if product_id not in subscribed_products:
        raise PermissionDenied("You are not subscribed to this product")
    
    return True



def get_user_lessons(user):
    bundle_choices = CourseBundleChoice.objects.filter(user=user).select_related("course_bundle")
    bundles = [choice.course_bundle for choice in bundle_choices]

    special_bundles = SpecialCourseBundle.objects.filter(course_bundle__in=bundles)
    for special_bundle in special_bundles:
        if not access_special_course(user, special_bundle.product_id):
            if special_bundle.course_bundle in bundles:
                bundles.remove(special_bundle.course_bundle)


    courses = Course.objects.filter(bundles__in=bundles).distinct()
   

    lessons = Lesson.objects.filter(course__in=courses).order_by("order").distinct()
    return lessons






def get_completed_level(user, course):
    lessons = get_user_lessons(user).filter(course=course)
    total_lessons = lessons.count()
    if total_lessons == 0:
        return 0

    completed = UserLessonCompletion.objects.filter(user=user, lesson__in=lessons).count()
    return round((completed / total_lessons) * 100, 2)


def lesson_permission(lesson, user):
    previous_lessons = Lesson.objects.filter(
        course=lesson.course,
        order__lt=lesson.order
    ).order_by("order")

    allowed_lessons = set(get_user_lessons(user))

    for prev in previous_lessons:
        if prev not in allowed_lessons:
            raise PermissionDenied(
                f"You do not have access to lesson {prev.order} - {prev.title}."
            )

        try:
            completion = UserLessonCompletion.objects.get(user=user, lesson=prev)
        except UserLessonCompletion.DoesNotExist:
            raise PermissionDenied(
                f"You must complete lesson {prev.order} - {prev.title} before accessing this one."
            )

        if completion.created_at:
            deadline = completion.created_at + timedelta(days=14)
            now = timezone.now()
            if now < deadline:
                waited = timesince(completion.created_at, now)
                remaining = timesince(now, deadline)
                raise PermissionDenied(
                    f"Lesson {prev.order} - {prev.title} is locked. \
                        You completed it {waited} ago. \
                        Please wait {remaining} more to unlock this lesson."
                )

    return True