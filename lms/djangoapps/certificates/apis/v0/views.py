""" API v0 views. """
import logging

from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from rest_framework import generics
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from certificates.models import GeneratedCertificate, CertificateStatuses
from .serializers import CertificateClassSerializer

from lms.djangoapps.certificates.api import get_certificate_for_user
from openedx.core.lib.api import (
    authentication,
    permissions,
)


log = logging.getLogger(__name__)


class CertificatesDetailView(GenericAPIView):
    """
        **Use Case**

            * Get the details of a certificate for a specific user in a course.

        **Example Request**

            GET /api/certificates/v0/certificates/{username}/courses/{course_id}

        **GET Parameters**

            A GET request must include the following parameters.

            * username: A string representation of an user's username.
            * course_id: A string representation of a Course ID.

        **GET Response Values**

            If the request for information about the Certificate is successful, an HTTP 200 "OK" response
            is returned.

            The HTTP 200 response has the following values.

            * username: A string representation of an user's username passed in the request.

            * course_id: A string representation of a Course ID.

            * certificate_type: A string representation of the certificate type.
                Can be honor|verified|professional

            * status: A string representation of the certificate status.

            * download_url: A string representation of the certificate url.

            * grade: A string representation of a float for the user's course grade.

        **Example GET Response**

            {
                "username": "bob",
                "course_id": "edX/DemoX/Demo_Course",
                "certificate_type": "verified",
                "status": "downloadable",
                "download_url": "http://www.example.com/cert.pdf",
                "grade": "0.98"
            }
    """

    authentication_classes = (
        authentication.OAuth2AuthenticationAllowInactiveUser,
        authentication.SessionAuthenticationAllowInactiveUser,
    )
    permission_classes = (
        IsAuthenticated,
        permissions.IsUserInUrlOrStaff
    )

    def get(self, request, username, course_id):
        """
        Gets a certificate information.

        Args:
            request (Request): Django request object.
            username (string): URI element specifying the user's username.
            course_id (string): URI element specifying the course location.

        Return:
            A JSON serialized representation of the certificate.
        """
        try:
            course_key = CourseKey.from_string(course_id)
        except InvalidKeyError:
            log.warning('Course ID string "%s" is not valid', course_id)
            return Response(
                status=404,
                data={'error_code': 'course_id_not_valid'}
            )

        user_cert = get_certificate_for_user(username=username, course_key=course_key)
        if user_cert is None:
            return Response(
                status=404,
                data={'error_code': 'no_certificate_for_user'}
            )
        return Response(
            {
                "username": user_cert.get('username'),
                "course_id": unicode(user_cert.get('course_key')),
                "certificate_type": user_cert.get('type'),
                "status": user_cert.get('status'),
                "download_url": user_cert.get('download_url'),
                "grade": user_cert.get('grade')
            }
        )


class UserCertificatesList(generics.ListAPIView):
    """
    ** Use cases **

        Request a list of certificate for a user, optionally constrained to a course.

    ** Example Requests **

        GET /api/certificates/v0/certificates/{username}/list

    ** Response Values **

        Body comprised of a list of objects with the following fields:

        * generated_certificate: The generated certificate of student and course. Represented as an object
          with the following fields:
            * course_id: The course key of the course this certificate is scoped to, or null if it isn't scoped to a course.
            * verify_uuid: The unique hashed string that identifies this generated certificate.
            * mode: The enrollment mode of student in course.
            * grade: The final grade of the student in the course.
            * created_date: The date the certificate was created.
            * image_url: A URL to the icon image used to represent this award, the course image.
            * display_name: The display name of the course.

    ** Returns **

        * 200 on success, with a list of Generated Certificate objects.
        * 403 if a user who does not have permission to masquerade as
          another user specifies a username other than their own.
        * 404 if the specified user does not exist

        {
            "count": 7,
            "previous": null,
            "num_pages": 1,
            "results": [
                {
                    "course_id": "course-v1:edX+DemoX+Demo_Course",
                    "verify_uuid": "3df0b2f277e24356bb016f8cddbd8d83",
                    "mode": "honor",
                    "grade": "0.83",
                    "created_date": "2018-08-06 15:42:37",
                    "image_url": "http://certificates.example.com/media/issued/cd75b69fc1c979fcc1697c8403da2bdf.png",
                    "display_name": "Course of Applied Informatics",
                },
            ...
            ]
        }
    """
    serializer_class = CertificateClassSerializer
    authentication_classes = (
        authentication.OAuth2AuthenticationAllowInactiveUser,
        authentication.SessionAuthenticationAllowInactiveUser
    )
    permission_classes = (
        IsAuthenticated,
        permissions.IsUserInUrlOrStaff
    )

    def filter_queryset(self, queryset):
        """
        Return most recent to least recent certificate.
        """
        return queryset.order_by('-created_date')

    def get_queryset(self):
        """
        Get all certificates for the username specified.
        """
        try:
            return GeneratedCertificate.objects.filter(user__username=self.kwargs['username'], status=CertificateStatuses.downloadable)
        except GeneratedCertificate.DoesNotExist:
            pass

        return None

