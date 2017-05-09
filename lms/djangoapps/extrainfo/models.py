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


class NationalID(models.Model):
    """
    The form that wraps this model is in the forms.py file.
    """
    user = models.OneToOneField(USER_MODEL, null=False)

    national_id = models.CharField(
        verbose_name="National Identification Number",
        max_length=30,
        unique=True,
    )

def get_dni(user_id):
    try:
        dni = ExtraInfo.objects.get(user=user_id)
    except ExtraInfo.DoesNotExist:
        dni = False
    return dni

def set_dni(request):
    if request.method == "POST":
        if request.user.is_authenticated():
            user = request.user.id
            username =  request.user.username
            try:
               identification = request.POST.get('identification')
               try:
                   user_identity = ExtraInfo.objects.get(national_id=identification)
               except ExtraInfo.DoesNotExist:
                   user_identity = False
               if identification == '':
                  return HttpResponse(json.dumps({'status': 'error'}), status=400)
               else:
                  if not user_identity:
                     new_id = ExtraInfo()
                     new_id.national_id = identification
                     new_id.user_id = user
                     new_id.save()
                  else:
                     raise Exception("No UserProfile related to user {0}".format(username))
            except Exception as exception:
                logger.error('Error thrown when updating Passport or National ID number of user {username}. ERROR: {exception}'.format(username=username, exception=exception))
                return HttpResponse(json.dumps({'status': 'error'}),status=400)
            return HttpResponse(json.dumps({'status': 'success'}),status=200)
    return HttpResponse(json.dumps({'status': 'error'}),  status=400)
