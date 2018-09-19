"""
Serializers for Badges
"""
from rest_framework import serializers

from badges.models import BadgeClass, BadgeAssertion
from django.contrib.auth.models import User
from xmodule.modulestore.django import modulestore
from student.models import CourseEnrollment
from lms.djangoapps.grades.new.course_grade import CourseGradeFactory
from django.utils.translation import ugettext_lazy as _

import logging

log = logging.getLogger(__name__)

class BadgeClassSerializer(serializers.ModelSerializer):
    """
    Serializer for BadgeClass model.
    """
    image_url = serializers.ImageField(source='image')

    class Meta(object):
        model = BadgeClass
        fields = ('slug', 'issuing_component', 'display_name', 'course_id', 'description', 'criteria', 'image_url')


class BadgeAssertionSerializer(serializers.ModelSerializer):
    """
    Serializer for the BadgeAssertion model.
    """
    badge_class = BadgeClassSerializer(read_only=True)
    grade = serializers.SerializerMethodField()

    class Meta(object):
        model = BadgeAssertion
        fields = ('badge_class', 'image_url', 'assertion_url', 'created', 'grade')

    def get_grade(self, badge_assertion):
        try:
            user_id = badge_assertion.user_id
            badge_class = BadgeClass.objects.get(id=badge_assertion.badge_class_id)
            course_id = badge_class.course_id
            student = User.objects.get(id=user_id)
            store = modulestore()
            course_key = course_id
            course = store.get_course(course_key, depth=0)
            course_grade = CourseGradeFactory().create(student, course, read_only=True)
            return str(course_grade.summary['percent'] * 100) + '%'
        except Exception as e:
            log.error('Excepction on getting grade of badge_assertion id "{assertion_id}". Error: {e}'.format(assertion_id=badge_assertion.id, e=e))
            pass
        return _(u"Not available")
