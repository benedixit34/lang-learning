from cloudinary_storage.validators import validate_video
from rest_framework import serializers

from app.accounts.models import Instructor
from app.accounts.serializers import InstructorReadSerializer
from drf_stripe.models import Subscription

from .models import Course, CourseBundle, Lesson, Video, CourseBundleChoice, UserLessonCompletion, UserCourseProgress

class CourseWriteSerializer(serializers.ModelSerializer):
    instructors = serializers.PrimaryKeyRelatedField(
        queryset=Instructor.objects.all(), many=True
    )

    class Meta:
        model = Course
        fields = ["name", "description", "language", "instructors"]

    def create(self, validated_data):
        instructors = validated_data.pop("instructors", [])
        course = Course.objects.create(**validated_data)
        course.instructors.set(instructors)
        return course


class CourseReadSerializer(serializers.ModelSerializer):
    instructors = InstructorReadSerializer(many=True)

    class Meta:
        model = Course
        fields = [
            "uuid",
            "name",
            "description",
            "language",
            "instructors",
        ]

   


class LessonWriteSerializer(serializers.ModelSerializer):
    course = serializers.UUIDField(write_only=True)

    class Meta:
        model = Lesson
        fields = [
            "course",
            "title",
            "description",
        ]

    def validate_course(self, value):
        try:
            return Course.objects.get(uuid=value)
        except Course.DoesNotExist:
            raise serializers.ValidationError("Course with this UUID does not exist.")

    def create(self, validated_data):
        course = validated_data.pop("course")
        lesson = Lesson.objects.create(course=course, **validated_data)
        return lesson


class VideoReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ["uuid", "name", "description", "video", "featured_image"]


class LessonRetrieveReadSerializer(serializers.ModelSerializer):
    video = VideoReadSerializer()

    class Meta:
        model = Lesson
        fields = [
            "uuid",
            "title",
            "description",
            "order",
            "video",
            "created_at",
            "updated_at",
        ]

class LessonListReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            "uuid",
            "title",
            "description",
            "order",
            "created_at",
            "updated_at",
        ]


class VideoWriteSerializer(serializers.ModelSerializer):
    lesson = serializers.UUIDField(write_only=True)
    video_file = serializers.FileField(validators=[validate_video])
    image_file = serializers.FileField()

    class Meta:
        model = Video
        fields = ["name", "lesson", "description", "video_file", "image_file"]

    def validate_lesson(self, value):
        try:
            Lesson.objects.get(uuid=value)
            return value
        except Lesson.DoesNotExist:
            raise serializers.ValidationError("Lesson with this UUID does not exist.")

    def create(self, validated_data):
        lesson = validated_data.pop("lesson")
        video = Video.objects.create(lesson=lesson, **validated_data)
        return lesson

    def validate_video_file(self, value):
        max_video_size = 100 * 1024 * 1024  # 100MB
        if value.size > max_video_size:
            raise serializers.ValidationError(
                "Video file too large. Maximum size is 100MB."
            )

        return value

    def validate_image_file(self, value):
        allowed_image_types = ["image/jpeg", "image/png"]
        if value.content_type not in allowed_image_types:
            raise serializers.ValidationError(
                "Invalid image file type. Allowed types: jpeg, png."
            )

        max_image_size = 5 * 1024 * 1024  # 5MB
        if value.size > max_image_size:
            raise serializers.ValidationError(
                "Image file too large. Maximum size is 5MB."
            )

        return value


class CourseBundleReadSerializer(serializers.ModelSerializer):
    courses = CourseReadSerializer(many=True)

    class Meta:
        model = CourseBundle
        fields = ["uuid", "name", "description", "courses"]



class CourseBundleWriteSerializer(serializers.ModelSerializer):
    courses = serializers.ListField(child=serializers.UUIDField(), write_only=True)

    class Meta:
        model = CourseBundle
        fields = ["name", "description", "courses"]

    def validate_courses(self, value):
        if not value:
            raise serializers.ValidationError("This field cannot be empty.")

        valid_courses = []
        for course_uuid in value:
            try:
                course = Course.objects.get(uuid=course_uuid)
                valid_courses.append(course)
            except Course.DoesNotExist:
                raise serializers.ValidationError(
                    f"Course with UUID {course_uuid} does not exist."
                )

        return valid_courses
    
    


    def create(self, validated_data):
        courses = validated_data.pop("courses")
        course_bundle = CourseBundle.objects.create(**validated_data)
        course_bundle.courses.set(courses)  # Set the ManyToMany relationship
        return course_bundle

class CourseBundleChoiceSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.email')
    course_bundle = serializers.PrimaryKeyRelatedField(queryset=CourseBundle.objects.all())

    class Meta:
        model = CourseBundleChoice
        fields = ['user', 'course_bundle']
    

class UserLessonCompletionSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.email')
    lesson = serializers.PrimaryKeyRelatedField(queryset=Lesson.objects.all())

    class Meta:
        model = UserLessonCompletion
        fields = ['user', 'lesson']

class UserCourseProgressSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.email')
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())

    class Meta:
        model = UserCourseProgress
        fields = ['user', 'course', 'completion_level']





