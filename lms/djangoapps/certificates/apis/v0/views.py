""" API v0 views. """
import logging

from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from rest_framework import generics
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from certificates.models import GeneratedCertificate
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

        GET /api/certificates/v1/user/{username}/list

    ** Response Values **

        Body comprised of a list of objects with the following fields:

        * certificate_class: The certificate class the assertion was awarded for. Represented as an object
          with the following fields:
            * slug: The identifier for the certificate class
            * issuing_component: The software component responsible for issuing this certificate.
            * display_name: The display name of the certificate.
            * course_id: The course key of the course this certificate is scoped to, or null if it isn't scoped to a course.
            * description: A description of the award and its significance.
            * criteria: A description of what is needed to obtain this award.
            * image_url: A URL to the icon image used to represent this award.
        * image_url: The baked assertion image derived from the certificate_class icon-- contains metadata about the award
          in its headers.
        * assertion_url: The URL to the OpenCertificates CertificateAssertion object, for verification by compatible tools
          and software.

    ** Params **

        * slug (optional): The identifier for a particular certificate class to filter by.
        * issuing_component (optional): The issuing component for a particular certificate class to filter by
          (requires slug to have been specified, or this will be ignored.) If slug is provided and this is not,
          assumes the issuing_component should be empty.
        * course_id (optional): Returns assertions that were awarded as part of a particular course. If slug is
          provided, and this field is not specified, assumes that the target certificate has an empty course_id field.
          '*' may be used to get all certificates with the specified slug, issuing_component combination across all courses.

    ** Returns **

        * 200 on success, with a list of Certificate Assertion objects.
        * 403 if a user who does not have permission to masquerade as
          another user specifies a username other than their own.
        * 404 if the specified user does not exist

        {
            "count": 7,
            "previous": null,
            "num_pages": 1,
            "results": [
                {
                    "certificate_class": {
                        "slug": "special_award",
                        "issuing_component": "openedx__course",
                        "display_name": "Very Special Award",
                        "course_id": "course-v1:edX+DemoX+Demo_Course",
                        "description": "Awarded for people who did something incredibly special",
                        "criteria": "Do something incredibly special.",
                        "image": "http://example.com/media/certificate_classes/certificates/special_xdpqpBv_9FYOZwN.png"
                    },
                    "image_url": "http://certificates.example.com/media/issued/cd75b69fc1c979fcc1697c8403da2bdf.png",
                    "assertion_url": "http://certificates.example.com/public/assertions/07020647-e772-44dd-98b7-d13d34335ca6"
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
            return GeneratedCertificate.objects.filter(user__username=self.kwargs['username'], status=GeneratedCertificate.downloadable)
        except GeneratedCertificate.DoesNotExist:
            pass

        return None

