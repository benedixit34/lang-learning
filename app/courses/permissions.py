from django.utils import timezone
from django.utils.timesince import timesince
from datetime import timedelta
from rest_framework.exceptions import PermissionDenied
from app.courses.models import Lesson, UserLessonCompletion
from app.courses.utils import get_user_lessons


from datetime import timedelta
from django.utils import timezone
from django.utils.timesince import timesince
from rest_framework.exceptions import PermissionDenied


from app.accounts.models import Instructor

def lesson_permission(lesson, user):
    # All previous lessons in order
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
                f"You must complete lesson {prev.order} - {prev.title} \
                    before accessing this one."
            )

        if completion.created_at:
            deadline = completion.created_at + timedelta(days=7)
            now = timezone.now()
            if now < deadline:
                waited = timesince(completion.created_at, now)
                remaining = timesince(now, deadline)
                raise PermissionDenied(
                    f"Lesson {prev.order} - {prev.title} is locked. "
                    f"You completed it {waited} ago. "
                    f"Please wait {remaining} more to unlock this lesson."
                )

    return True


def is_instructor(user):
    return Instructor.objects.filter(user=user).exists()