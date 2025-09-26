from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from app.accounts.models import Instructor
from app.general.models import CreatedUpdated
from drf_stripe.models import Product

User = get_user_model()

# Model defining courses available on the platform
class Course(CreatedUpdated):
    name = models.CharField(max_length=100)
    description = models.TextField()
    language = models.CharField(max_length=50)
    instructors = models.ManyToManyField(Instructor, related_name="courses")

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ["-created_at"]


class CourseBundle(CreatedUpdated):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    courses = models.ManyToManyField(Course, related_name="bundles")


    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-created_at"]


class SpecialCourseBundle(CreatedUpdated):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    course_bundle = models.ForeignKey(CourseBundle, on_delete=models.CASCADE)


class CourseBundleChoice(CreatedUpdated):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course_bundle = models.ForeignKey(CourseBundle, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.email} access to {self.course_bundle.name}"
    
    class Meta:
        unique_together = ('user', 'course_bundle')


class Section(CreatedUpdated):
    name = models.CharField(max_length=100)
    course = models.ForeignKey(
        Course, related_name="sections", on_delete=models.SET_NULL, null=True
    )
    order = models.IntegerField()

    def __str__(self):
        return f"{self.course.name}-{self.name}"

    class Meta:
        ordering = ["order"]


# Model representing individual lessons within a course
class Lesson(CreatedUpdated):
    course = models.ForeignKey(Course, related_name="lessons", on_delete=models.CASCADE)
    section = models.ForeignKey(
        Section, on_delete=models.SET_NULL, null=True, related_name="lessons"
    )
    title = models.CharField(max_length=100)
    description = models.TextField()
    order = models.IntegerField()

    def __str__(self):
        return f"{self.title}-{self.course.name}"

    class Meta:
        ordering = ["order"]


class Video(CreatedUpdated):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=False, null=False)
    description = models.TextField()
    video = models.URLField(max_length=250)
    featured_image = models.URLField(max_length=250)

    def __str__(self):
        return self.name


class UserCourseProgress(CreatedUpdated):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    completion_level = models.FloatField(default=0.0)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.email} - {self.course.name} - Completion: {self.completion_level}%"


class UserLessonCompletion(CreatedUpdated):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'lesson')

    def __str__(self):
        return f"{self.user.email} has completed {self.lesson.title}"