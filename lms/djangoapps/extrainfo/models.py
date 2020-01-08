from django.conf import settings
from django.db import models

# Backwards compatible settings.AUTH_USER_MODEL
USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


class NationalId(models.Model):
    """
    The form that wraps this model is in the forms.py file.
    """
    user = models.OneToOneField(USER_MODEL, null=False)

    national_id = models.CharField(
        verbose_name="National Identification Number",
        max_length=30,
        unique=True,
    )

    def get_national_id(self):
        try:
            national_id = self.national_id
        except NationalId.DoesNotExist:
            national_id = False
        return national_id

    def set_national_id(self,user,identification=None):
        self.user = user
        self.national_id = identification
        self.save()


    def __unicode__(self):
        return self.user.username
