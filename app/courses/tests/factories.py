import factory

from app.accounts.tests.factories import CustomUserFactory
from app.courses.models import Course, Lesson, UserVideoAccess, Video


class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Course

    name = "Sample Course"
    description = "Description of the sample course."
    language = "English"
    price = 50.00


class LessonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Lesson

    course = factory.SubFactory(CourseFactory)
    title = "Sample Lesson"
    description = "Description of the sample lesson."
    order = 1


class VideoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Video

    course = factory.SubFactory(CourseFactory)
    name = "Sample Video"
    description = "Description of the sample video."
    video = factory.django.ImageField(filename="sample_video.mp4")
    featured_image = factory.django.ImageField(filename="sample_image.png")
    order = 1


class UserVideoAccessFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserVideoAccess

    user = factory.SubFactory(CustomUserFactory)
    video = factory.SubFactory(VideoFactory)
    access_date = factory.Faker("date")
    access_count = 0
