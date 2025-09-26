from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status

from drf_stripe.models import Subscription, StripeUser, SubscriptionItem, Product, Price
from .models import CourseBundleChoice, Video, Lesson, UserLessonCompletion, Course, SpecialCourseBundle
from django.shortcuts import get_object_or_404

class SubscriptionMixin:

    def check_paystack_subscription(self, user):
        pass



    def get_courses(self, user):
        bundle_choices = CourseBundleChoice.objects.filter(user=user).prefetch_related('course_bundle__courses').all()
        
        special_bundle_product = SpecialCourseBundle.objects.all()

        products = []
        special_bundles = []
        for bundle_product in special_bundle_product:
            if hasattr(bundle_product, 'product') and bundle_product.product:
                products.append(bundle_product.product.name)
            
            if hasattr(bundle_product, 'course_bundle') and bundle_product.course_bundle:
                special_bundles.append(bundle_product.course_bundle)
        
        special_bundle_choice = CourseBundleChoice.objects.filter(
            user=user, course_bundle__in = special_bundles).first()
        
        regular_bundle_choice = CourseBundleChoice.objects.filter(user=user).exclude(
            course_bundle__in=special_bundles).first()

        regular_products = Product.objects.filter(active=True).exclude(name__in=products)
        special_products = Product.objects.filter(name__in=products, active=True)
       
        has_special_access = self.access_course(user, products=special_products)
        has_regular_access = self.access_course(user, products=regular_products)


        if has_special_access and has_regular_access:
            return [course for bundle_choice in bundle_choices for course in bundle_choice.course_bundle.courses.all()] 
        elif has_regular_access:
            return regular_bundle_choice.course_bundle.courses.all()
        elif has_special_access:
            return special_bundle_choice.course_bundle.courses.all()
        else:
            return Course.objects.none
            


    def access_course(self, user, products):
        stripe_user = get_object_or_404(StripeUser, user=user)
        prices = Price.objects.filter(product__in=products, active=True)
        subscriptions = Subscription.objects.filter(stripe_user=stripe_user, status="active")

        if subscriptions.exists():
           if SubscriptionItem.objects.filter(subscription__in=subscriptions, price__in=prices).exists():
                return Response({"detail": "You have access to course"}, status=status.HTTP_200_OK)
        else:
            raise PermissionDenied("You do not have permission to view this course")


    def get_allowed_lessons(self, user):
        if CourseBundleChoice.objects.filter(user=user).exists():
            courses = self.get_courses(user)
            return Lesson.objects.filter(course__in=courses)
        else:
            raise PermissionDenied("Please select a course bundle.")
        
    def get_allowed_videos(self, user):
        if CourseBundleChoice.objects.filter(user=user).exists():
            lessons = self.get_allowed_lessons(user).all()
            return Video.objects.filter(lesson__in=lessons).order_by('created_at')
        else:
            raise PermissionDenied("Please select a course bundle.")
        

    
    def get_completed_level(self, user, course):
        all_lessons = self.get_allowed_lessons(user).filter(course=course)
        all_lessons_num = all_lessons.count()
        completed_lessons = UserLessonCompletion.objects.filter(user=self.request.user, lesson__in=all_lessons)
        completed_lessons_num = completed_lessons.count()
        completion_level = (completed_lessons_num / all_lessons_num) * 100
        return completion_level
        


    def check_subscription(self, user):
        print(f"Checking subscription for user: {user}")
        try:
            stripe_user = get_object_or_404(StripeUser, user=user)
            print(f"Found StripeUser: {stripe_user}")
            return Subscription.objects.filter(stripe_user=stripe_user, status="active").exists()
        except Exception as e:
            print(f"Error: {e}")
            raise