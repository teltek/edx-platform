""" Certificates API v0 URLs. """

from django.conf import settings
from django.conf.urls import (
    include,
    patterns,
    url,
)

from lms.djangoapps.certificates.apis.v0 import views


CERTIFICATES_URLS = patterns(
    '',
    url(
        r'^{username}/courses/{course_id}/$'.format(
            username=settings.USERNAME_PATTERN,
            course_id=settings.COURSE_ID_PATTERN
        ),
        views.CertificatesDetailView.as_view(), name='detail'
    ),
    url(
        r'^{username}/list/$'.format(
            username=settings.USERNAME_PATTERN
        ),
        views.UserCertificatesList.as_view(), name='user_certificates_list'
    ),
)

urlpatterns = patterns(
    '',
    url(r'^certificates/', include(CERTIFICATES_URLS, namespace='certificates')),
)
