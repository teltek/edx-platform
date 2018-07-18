from django.db import models
from django.conf import settings

# Backwards compatible settings.AUTH_USER_MODEL
USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')

class NationalId(models.Model):
    """
    This model contains two extra fields that will be saved when a user registers.
    The form that wraps this model is in the forms.py file.
    """
    user = models.OneToOneField(USER_MODEL, null=False)
    national_id = models.CharField(
        verbose_name="National Identification Number",
        max_length=30,
        unique=True,
    )
