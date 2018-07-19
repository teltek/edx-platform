from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

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

    @classmethod
    def get_from_user(cls, user):
        if type(user) == str:
            try:
                user = User.objects.get(username=request.user)
            except Exception:
                return False
        try:
            return cls.objects.get(user=user)
        except cls.DoesNotExist:
            return False
        except Exception as exception:
            log.error('exception: {}'.format(exception))
            return False

    @classmethod
    def create(cls, user, national_id):
        instance = cls.objects.create(user=user,national_id=national_id)
        instance.save()
        return instance
