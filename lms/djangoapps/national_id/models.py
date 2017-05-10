import logging
import json
from django.conf import settings
from django.db import models
from django.http import (
        HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpRequest
)
from student.models import UserProfile

logger = logging.getLogger(__name__)

# Backwards compatible settings.AUTH_USER_MODEL
USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


class ExtraInfo(models.Model):
    """
    The form that wraps this model is in the forms.py file.
    """
    user = models.OneToOneField(USER_MODEL, null=True)

    national_id = models.CharField(
        verbose_name="National Identification Number",
        max_length=30,
        unique=True,
    )

    def get_dni(self):
        try:
            dni = self.national_id
        except ExtraInfo.DoesNotExist:
            dni = False
        return dni

    def set_dni(self,user,identification=None):
        self.user = user
        self.national_id = identification
        self.save()
