from django.contrib import admin

# Register your models here.
from .models import Course, CourseBundle, Lesson, \
    Section, Video, CourseBundleChoice, UserLessonCompletion, \
    UserCourseProgress, SpecialCourseBundle

admin.site.register(Course)
admin.site.register(CourseBundle)
admin.site.register(Lesson)
admin.site.register(Section)
admin.site.register(Video)
admin.site.register(CourseBundleChoice)
admin.site.register(UserLessonCompletion)
admin.site.register(UserCourseProgress)
admin.site.register(SpecialCourseBundle)
