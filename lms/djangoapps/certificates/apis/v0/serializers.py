"""
Serializers for Certificates
"""
from rest_framework import serializers

from certificates.models import GeneratedCertificate
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

import logging

log = logging.getLogger(__name__)

class CertificateClassSerializer(serializers.ModelSerializer):
    """
    Serializer for CertificateClass model.
    """
    image_url = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()

    class Meta(object):
        model = GeneratedCertificate
        fields = ('course_id', 'verify_uuid', 'mode', 'grade', 'created_date', 'image_url', 'display_name')

    def get_image_url(self, certificate):
        try:
            course_overview = CourseOverview.get_from_id(certificate.course_id)
            return course_overview.image_urls['small']
        except Exception as excep:
            log.warning('There was an exception on get course overview: {0}'.format(excep.message))
        return 'ImageNotFound'

    def get_display_name(self, certificate):
        try:
            course_overview = CourseOverview.get_from_id(certificate.course_id)
            return course_overview.display_name
        except Exception as excep:
            log.warning('There was an exception on get course overview: {0}'.format(excep.message))
        return 'Course Not Found'
