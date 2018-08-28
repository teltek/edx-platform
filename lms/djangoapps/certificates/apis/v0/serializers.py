"""
Serializers for Certificates
"""
from rest_framework import serializers

from certificates.models import GeneratedCertificate


class CertificateClassSerializer(serializers.ModelSerializer):
    """
    Serializer for CertificateClass model.
    """
    class Meta(object):
        model = GeneratedCertificate
        fields = ('course_id', 'verify_uuid', 'mode', 'created_date')
